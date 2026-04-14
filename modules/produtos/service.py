from .repository import (
    listar_produtos_db,
    upsert_produto_db
)

import requests

def listar_produtos_service():
    produtos = listar_produtos_db()

    return {
        "ok": True,
        "produtos": produtos
    }

def sync_produto_service(data):
    upsert_produto_db(data)


def resgatar_produto_service(data):

    response = requests.post(
        "http://localhost:5000/comandas/adicionar-item-clube",
        json={
            "numero_comanda": data["comanda_id"],
            "item_id": data["item_id"]
        },
        headers={
            "x-api-key": "comandas_api_key_qualquer_coisa_longa_e_segura"
        },
        timeout=2
    )

    # 🚨 valida resposta do Caixa
    if response.status_code != 200:
        raise Exception(f"Erro no Caixa: {response.text}")

    return {"ok": True}


