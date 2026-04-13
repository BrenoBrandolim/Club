from .repository import (
    buscar_produto_por_id_db,
    criar_resgate_db,
    debitar_pontos_db
)

from modules.usuarios.repository import buscar_usuario_por_id

from modules.pontos.repository import calcular_saldo_usuario_db


def resgatar_produto_service(usuario_id, produto_id, comanda_id):

    # 1. usuário existe?
    usuario = buscar_usuario_por_id(usuario_id)
    if not usuario:
        return {"ok": False, "message": "Usuário não encontrado"}

    # 2. produto existe?
    produto = buscar_produto_por_id_db(produto_id)
    if not produto:
        return {"ok": False, "message": "Produto não encontrado"}

    # 3. produto ativo?
    if not produto['ativo']:
        return {"ok": False, "message": "Produto indisponível"}

    # 4. saldo
    saldo = calcular_saldo_usuario_db(usuario_id)

    # 5. tem pontos?
    if saldo < produto['pontos_necessarios']:
        return {"ok": False, "message": "Pontos insuficientes"}

    # 6. cria resgate
    resgate_id = criar_resgate_db(
        usuario_id,
        produto_id,
        comanda_id,
        produto['pontos_necessarios']
    )

    # 7. debita pontos
    debitar_pontos_db(
        usuario_id,
        produto['pontos_necessarios'],
        comanda_id
    )

    return {
        "ok": True,
        "message": "Resgate realizado com sucesso",
        "resgate_id": resgate_id
    }