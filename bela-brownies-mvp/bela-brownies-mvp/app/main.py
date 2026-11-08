"""Bela Brownies MVP — rotas e regras de negócio."""
import logging
import time
from collections import defaultdict
from datetime import date

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import config, db, security

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bela")

app = FastAPI(title="Bela Brownies", docs_url=None if config.IS_PRODUCTION else "/docs",
              redoc_url=None, openapi_url=None if config.IS_PRODUCTION else "/openapi.json")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

STATUS = {"pendente": "Pendente", "em_producao": "Em produção",
          "pronto": "Pronto", "entregue": "Entregue"}


# ---------- autenticação ----------
class NotAuthenticated(Exception):
    pass


@app.exception_handler(NotAuthenticated)
async def _not_auth(request: Request, exc: NotAuthenticated):
    return RedirectResponse("/login", status_code=303)


def current_user(request: Request) -> str:
    user = security.read_token(request.cookies.get("token"))
    if user is None:
        raise NotAuthenticated()
    return user


_tentativas: dict[str, list[float]] = defaultdict(list)


def _bloqueado(ip: str) -> bool:
    agora = time.time()
    _tentativas[ip] = [t for t in _tentativas[ip] if agora - t < 300]
    return len(_tentativas[ip]) >= 5  # 5 falhas em 5 minutos


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"erro": None})


@app.post("/login")
async def login(request: Request, usuario: str = Form(...), senha: str = Form(...)):
    ip = request.client.host if request.client else "?"
    if _bloqueado(ip):
        return templates.TemplateResponse(request, "login.html",
            {"erro": "Muitas tentativas. Aguarde 5 minutos e tente de novo."}, status_code=429)
    ok = usuario == config.ADMIN_USER and security.verify_password(senha, config.ADMIN_PASSWORD_HASH)
    if not ok:
        _tentativas[ip].append(time.time())
        return templates.TemplateResponse(request, "login.html",
            {"erro": "Usuário ou senha incorretos."}, status_code=401)
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie("token", security.create_token(usuario), httponly=True, samesite="lax",
                    secure=config.IS_PRODUCTION, max_age=config.TOKEN_MINUTES * 60)
    return resp


@app.get("/logout")
async def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie("token")
    return resp


# ---------- telas ----------
@app.get("/")
async def menu(request: Request, user: str = Depends(current_user)):
    pedidos = db.listar_pedidos()
    criticos = [i for i in db.listar_insumos()
                if float(i["quantidade_atual"]) <= float(i["limite_minimo"])]
    return templates.TemplateResponse(request, "menu.html", {
        "user": user, "pedidos": pedidos, "criticos": criticos, "status": STATUS,
        "hoje": date.today().strftime("%d/%m/%Y")})


@app.get("/pedidos/novo")
async def novo_pedido(request: Request, user: str = Depends(current_user)):
    return templates.TemplateResponse(request, "pedido_novo.html", {
        "insumos": db.listar_insumos(), "erro": None, "hoje": date.today().isoformat()})


@app.post("/pedidos")
async def salvar_pedido(request: Request, user: str = Depends(current_user)):
    form = await request.form()
    cliente = str(form.get("cliente", "")).strip()
    descricao = str(form.get("descricao", "")).strip()
    entrega = str(form.get("data_entrega", "")).strip()
    insumos = db.listar_insumos()

    def erro(msg: str):
        return templates.TemplateResponse(request, "pedido_novo.html", {
            "insumos": insumos, "erro": msg, "hoje": date.today().isoformat(),
            "v": {"cliente": cliente, "descricao": descricao, "data_entrega": entrega}},
            status_code=400)

    # validação no servidor (RNF02)
    if not cliente or not descricao or not entrega:
        return erro("Preencha cliente, descrição e data de entrega.")
    if len(cliente) > 120 or len(descricao) > 800:
        return erro("Texto longo demais. Reduza o nome ou a descrição.")
    try:
        if date.fromisoformat(entrega) < date.today():
            return erro("A data de entrega não pode ser anterior a hoje.")
    except ValueError:
        return erro("Data de entrega inválida.")

    itens = []
    for ins in insumos:
        bruto = str(form.get(f"insumo_{ins['id']}", "")).strip().replace(",", ".")
        if not bruto:
            continue
        try:
            qtd = float(bruto)
        except ValueError:
            return erro(f"Quantidade inválida para {ins['nome_insumo']}.")
        if qtd < 0:
            return erro(f"Quantidade negativa para {ins['nome_insumo']}.")
        if qtd > 0:
            itens.append({"insumo_id": ins["id"], "quantidade": qtd})

    try:
        db.criar_pedido(cliente, descricao, entrega, itens)  # transação atômica
    except Exception:
        log.exception("Falha ao criar pedido")
        return erro("Não foi possível salvar. Confira se há estoque suficiente e tente de novo.")
    return RedirectResponse("/?ok=pedido", status_code=303)


@app.post("/pedidos/{pedido_id}/status")
async def mudar_status(pedido_id: int, status: str = Form(...), user: str = Depends(current_user)):
    if status in STATUS:
        db.atualizar_status(pedido_id, status)
    return RedirectResponse("/", status_code=303)


@app.get("/estoque")
async def estoque(request: Request, user: str = Depends(current_user)):
    return templates.TemplateResponse(request, "estoque.html", {"insumos": db.listar_insumos()})


@app.post("/estoque/repor")
async def repor(insumo_id: int = Form(...), quantidade: float = Form(...),
                user: str = Depends(current_user)):
    if quantidade > 0:
        db.repor_insumo(insumo_id, quantidade)
    return RedirectResponse("/estoque", status_code=303)


@app.post("/estoque/novo")
async def novo_insumo(nome: str = Form(...), quantidade: float = Form(...),
                      unidade: str = Form(...), minimo: float = Form(...),
                      user: str = Depends(current_user)):
    if nome.strip() and quantidade >= 0 and minimo >= 0:
        db.adicionar_insumo(nome.strip()[:120], quantidade, unidade.strip()[:20], minimo)
    return RedirectResponse("/estoque", status_code=303)


@app.exception_handler(Exception)
async def _erro_generico(request: Request, exc: Exception):
    log.exception("Erro não tratado")  # detalhes só no log, nunca na tela
    return templates.TemplateResponse(request, "login.html",
        {"erro": "Algo deu errado. Tente novamente em instantes."}, status_code=500)
