"""Camada de persistência (Supabase/PostgreSQL). Sem SQL concatenado: o
cliente usa chamadas parametrizadas (RNF02 / OWASP A03)."""
from supabase import create_client, Client
from app import config

_client: Client | None = None


def client() -> Client:
    global _client
    if _client is None:
        _client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
    return _client


def listar_insumos():
    return client().table("insumos").select("*").order("nome_insumo").execute().data


def adicionar_insumo(nome: str, quantidade: float, unidade: str, minimo: float):
    client().table("insumos").insert({
        "nome_insumo": nome, "quantidade_atual": quantidade,
        "unidade_medida": unidade, "limite_minimo": minimo,
    }).execute()


def repor_insumo(insumo_id: int, quantidade: float):
    atual = client().table("insumos").select("quantidade_atual").eq("id", insumo_id).single().execute().data
    client().table("insumos").update(
        {"quantidade_atual": float(atual["quantidade_atual"]) + quantidade}
    ).eq("id", insumo_id).execute()


def listar_pedidos(limite: int = 30):
    return (client().table("pedidos").select("*")
            .neq("status", "entregue").order("data_entrega").limit(limite).execute().data)


def criar_pedido(cliente: str, descricao: str, data_entrega: str, itens: list[dict]):
    return client().rpc("criar_pedido", {
        "p_cliente": cliente, "p_descricao": descricao,
        "p_data_entrega": data_entrega, "p_itens": itens,
    }).execute()


def atualizar_status(pedido_id: int, status: str):
    client().table("pedidos").update({"status": status}).eq("id", pedido_id).execute()
