"""
modules/pontos/service.py
"""
from .repository import buscar_saldo_db, registrar_pontos_db, historico_pontos_db, vincular_comanda_db


def saldo_service(usuario_id: int) -> dict:
    saldo = buscar_saldo_db(usuario_id)
    return {"ok": True, "saldo": saldo}


def historico_service(usuario_id: int) -> dict:
    historico = historico_pontos_db(usuario_id)
    return {"ok": True, "historico": [
        {**h, "valor": float(h["valor"]), "data_criacao": str(h["data_criacao"])}
        for h in historico
    ]}


def creditar_pontos_service(usuario_id: int, valor: float, comanda_id: int | None, descricao: str):
    registrar_pontos_db(usuario_id, "ganho", valor, comanda_id, descricao)


def debitar_pontos_service(usuario_id: int, valor: float, comanda_id: int | None, descricao: str):
    saldo = buscar_saldo_db(usuario_id)
    if saldo < valor:
        raise ValueError("Pontos insuficientes")
    registrar_pontos_db(usuario_id, "gasto", valor, comanda_id, descricao)


def vincular_comanda_service(usuario_id: int, comanda_id: int) -> dict:
    vincular_comanda_db(usuario_id, comanda_id)
    return {"ok": True, "message": "Comanda vinculada com sucesso"}
