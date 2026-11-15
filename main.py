from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="Bela Brownies MVP")

# Banco de dados em memória para demonstração funcional do MVP
estoque = [
    {"id": 1, "nome": "Chocolate Nobre", "desc": "Callets - Amargo 70%", "qtd": 12, "unidade": "kg", "minimo": 5},
    {"id": 2, "nome": "Farinha de Trigo", "desc": "Orgânica - Alta Qualidade", "qtd": 18, "unidade": "kg", "minimo": 5},
    {"id": 3, "nome": "Embalagem Caixa P", "desc": "Caixas de presente de Brownie - Pequena", "qtd": 2, "unidade": "un", "minimo": 5},
]

pedidos = []

BASE_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bela Brownies - Painel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #F7EFEA; font-family: system-ui, -apple-system, sans-serif; }}
        .bg-marrom {{ background-color: #5C3A21; }}
        .text-marrom {{ color: #4A2E1B; }}
        .bg-rosa {{ background-color: #F4C7CE; }}
        .border-marrom {{ border-color: #5C3A21; }}
    </style>
</head>
<body class="flex justify-center min-h-screen">
    <div class="w-full max-w-md bg-[#FAF5F2] min-h-screen shadow-xl flex flex-col justify-between border-x border-[#E8D8CE]">
        <!-- Cabeçalho -->
        <div>
            <div class="bg-[#F5E1E4] p-5 text-center border-b-4 border-[#5C3A21]">
                <h1 class="text-2xl font-serif font-bold text-marrom">{titulo}</h1>
                <p class="text-sm text-marrom opacity-80">{subtitulo}</p>
            </div>
            
            <!-- Conteúdo Dinâmico -->
            <div class="p-5">
                {conteudo}
            </div>
        </div>

        <!-- Barra de Navegação Inferior (Acessível: alvos >= 44px) -->
        <nav class="bg-white border-t border-[#E8D8CE] flex justify-around py-2 sticky bottom-0">
            <a href="/" class="flex flex-col items-center justify-center min-w-[64px] min-h-[48px] text-marrom font-semibold text-xs">
                <span class="text-lg">🏠</span>
                <span>Início</span>
            </a>
            <a href="/novo-pedido" class="flex flex-col items-center justify-center min-w-[64px] min-h-[48px] text-marrom font-semibold text-xs">
                <span class="text-lg">📋</span>
                <span>Pedidos ({total_pedidos})</span>
            </a>
            <a href="/estoque" class="flex flex-col items-center justify-center min-w-[64px] min-h-[48px] text-marrom font-semibold text-xs">
                <span class="text-lg">📦</span>
                <span>Estoque</span>
            </a>
        </nav>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def menu_inicial():
    conteudo = """
    <div class="space-y-4 mt-2">
        <a href="/novo-pedido" class="flex items-center justify-between bg-marrom text-white p-5 rounded-3xl shadow-md hover:opacity-95 transition min-h-[80px]">
            <div class="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center text-2xl font-bold">+</div>
            <div class="text-right">
                <span class="block text-xl font-bold">Novo Pedido</span>
                <span class="text-xs text-white/80">Registrar encomenda</span>
            </div>
        </a>

        <a href="/estoque" class="flex items-center justify-between bg-rosa text-marrom p-5 rounded-3xl shadow-md hover:opacity-95 transition min-h-[80px]">
            <div class="w-12 h-12 rounded-full bg-marrom text-white flex items-center justify-center text-xl">📦</div>
            <div class="text-right">
                <span class="block text-xl font-bold">Ver Estoque</span>
                <span class="text-xs text-marrom/80">Insumos e alertas</span>
            </div>
        </a>

        <div class="grid grid-cols-2 gap-3 pt-2">
            <div class="bg-white p-4 rounded-2xl border border-[#E8D8CE] flex items-center gap-3 min-h-[56px]">
                <span class="text-xl">📊</span>
                <span class="text-xs font-bold text-marrom">Relatórios de Vendas</span>
            </div>
            <div class="bg-white p-4 rounded-2xl border border-[#E8D8CE] flex items-center gap-3 min-h-[56px]">
                <span class="text-xl">👥</span>
                <span class="text-xs font-bold text-marrom">Clientes</span>
            </div>
        </div>
    </div>
    """
    return BASE_HTML.format(
        titulo="Olá, Isabela!",
        subtitulo="Bela Brownies - Painel",
        conteudo=conteudo,
        total_pedidos=len(pedidos)
    )

@app.get("/novo-pedido", response_class=HTMLResponse)
def tela_novo_pedido(sucesso: bool = False):
    alerta = ""
    if sucesso:
        alerta = """
        <div class="bg-green-100 border-l-4 border-green-600 text-green-900 p-3 mb-4 rounded-r text-sm font-medium">
            ✅ Pedido salvo! Baixa automática aplicada na Embalagem Caixa P.
        </div>
        """

    lista_recentes = ""
    if pedidos:
        itens_html = "".join([
            f"<li class='text-xs bg-white p-2.5 rounded-lg border border-[#E8D8CE]'><strong>{p['cliente']}</strong> ({p['data']}): {p['descricao']}</li>"
            for p in reversed(pedidos)
        ])
        lista_recentes = f"<div class='mt-6'><h3 class='text-sm font-bold text-marrom mb-2'>Pedidos Registrados:</h3><ul class='space-y-2'>{itens_html}</ul></div>"

    conteudo = f"""
    {alerta}
    <form action="/novo-pedido" method="post" class="space-y-4">
        <div>
            <label for="cliente" class="block text-sm font-bold text-marrom mb-1">Cliente</label>
            <input type="text" id="cliente" name="cliente" required placeholder="Digite o nome do cliente..."
                class="w-full p-3 rounded-xl border-2 border-marrom bg-white text-marrom min-h-[48px]">
        </div>

        <div>
            <label for="descricao" class="block text-sm font-bold text-marrom mb-1">Descrição do Pedido</label>
            <textarea id="descricao" name="descricao" rows="3" required placeholder="Ex: 12 mini brownies de brigadeiro..."
                class="w-full p-3 rounded-xl border-2 border-marrom bg-white text-marrom"></textarea>
        </div>

        <div>
            <label for="data_entrega" class="block text-sm font-bold text-marrom mb-1">Data de Entrega</label>
            <input type="date" id="data_entrega" name="data_entrega" required value="2026-11-15"
                class="w-full p-3 rounded-xl border-2 border-marrom bg-white text-marrom min-h-[48px]">
        </div>

        <button type="submit" class="w-full bg-marrom text-white font-bold py-3.5 rounded-xl shadow-md hover:opacity-95 transition min-h-[52px] tracking-wide">
            SALVAR PEDIDO
        </button>
    </form>
    {lista_recentes}
    """
    return BASE_HTML.format(
        titulo="NOVO PEDIDO",
        subtitulo="Bela Brownies - Painel",
        conteudo=conteudo,
        total_pedidos=len(pedidos)
    )

@app.post("/novo-pedido")
def salvar_pedido(cliente: str = Form(...), descricao: str = Form(...), data_entrega: str = Form(...)):
    pedidos.append({"cliente": cliente, "descricao": descricao, "data": data_entrega})
    # Simula baixa automática no estoque de embalagens
    for item in estoque:
        if item["id"] == 3 and item["qtd"] > 0:
            item["qtd"] -= 1
    return RedirectResponse(url="/novo-pedido?sucesso=true", status_code=303)

@app.get("/estoque", response_class=HTMLResponse)
def tela_estoque():
    cards = ""
    for item in estoque:
        critico = item["qtd"] <= item["minimo"]
        if critico:
            badge = """
            <span class="inline-flex items-center gap-1.5 bg-red-100 text-red-800 border border-red-300 px-3 py-1 rounded-lg text-xs font-extrabold" role="alert">
                <span>⚠️</span> CRÍTICO
            </span>
            """
            barra = '<div class="w-full bg-red-100 h-2.5 rounded-full mt-2"><div class="bg-red-600 h-2.5 rounded-full" style="width: 15%"></div></div>'
        else:
            badge = """
            <span class="inline-flex items-center gap-1.5 bg-green-100 text-green-800 border border-green-300 px-3 py-1 rounded-lg text-xs font-bold">
                <span>✅</span> Normal
            </span>
            """
            barra = '<div class="w-full bg-green-100 h-2.5 rounded-full mt-2"><div class="bg-green-600 h-2.5 rounded-full" style="width: 85%"></div></div>'

        cards += f"""
        <div class="bg-white p-4 rounded-2xl border border-[#E8D8CE] shadow-sm">
            <h2 class="text-lg font-bold text-marrom">{item['nome']}</h2>
            <p class="text-xs text-gray-600 mb-3">{item['desc']}</p>
            <div class="flex items-center justify-between">
                <span class="text-xl font-extrabold text-marrom">{item['qtd']} {item['unidade']}</span>
                {badge}
            </div>
            {barra}
        </div>
        """

    conteudo = f"<div class='space-y-4'>{cards}</div>"
    return BASE_HTML.format(
        titulo="Painel de Estoque",
        subtitulo="Bela Brownies",
        conteudo=conteudo,
        total_pedidos=len(pedidos)
    )