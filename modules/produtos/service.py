from .repository import (
    listar_produtos_db,
    upsert_produto_db
)

def listar_produtos_service():
    produtos = listar_produtos_db()

    return {
        "ok": True,
        "produtos": produtos
    }

def sync_produto_service(data):
    upsert_produto_db(data)