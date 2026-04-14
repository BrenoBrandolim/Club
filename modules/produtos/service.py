from .repository import (
    listar_produtos_db
)

def listar_produtos_service():
    produtos = listar_produtos_db()

    return {
        "ok": True,
        "produtos": produtos
    }