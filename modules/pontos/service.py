from .repository import (
    calcular_saldo_usuario_db
)

def obter_saldo_usuario_service(usuario_id):
    saldo = calcular_saldo_usuario_db(usuario_id)

    return {
        "ok": True,
        "saldo": float(saldo)
    }