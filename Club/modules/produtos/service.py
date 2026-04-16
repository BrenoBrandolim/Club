"""
modules/produtos/service.py
"""
from .repository import listar_produtos_db, buscar_produto_por_id_db, upsert_produto_db, editar_produto_db


def listar_produtos_service() -> list:
    return listar_produtos_db()


def buscar_produto_service(produto_id: int) -> dict | None:
    return buscar_produto_por_id_db(produto_id)


def sincronizar_produto_service(item_id, nome, pontos, preco_dinheiro, foto_url):
    upsert_produto_db(item_id, nome, float(pontos or 0), float(preco_dinheiro or 0), foto_url or "")


def editar_produto_service(produto_id, nome, foto_url, pontos, ativo):
    editar_produto_db(produto_id, nome, foto_url, float(pontos), bool(ativo))
