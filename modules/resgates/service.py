from .repository import (
    buscar_produto_por_id_db,
    criar_resgate_db,
    debitar_pontos_db,
    listar_resgates_usuario_db
)

from modules.comandas.repository import buscar_vinculo_completo_db
from modules.usuarios.repository import buscar_usuario_por_id

from modules.pontos.repository import calcular_saldo_usuario_db


from db.connection import get_connection

def resgatar_produto_service(usuario_id, produto_id, comanda_id):

    conn = get_connection()

    try:
        # 1. usuário existe?
        usuario = buscar_usuario_por_id(usuario_id)
        if not usuario:
            return {"ok": False, "message": "Usuário não encontrado"}

        # 2. produto existe?
        produto = buscar_produto_por_id_db(produto_id)
        if not produto:
            return {"ok": False, "message": "Produto não encontrado"}

        # 3. ativo?
        if not produto['ativo']:
            return {"ok": False, "message": "Produto indisponível"}

        # 3.5 validar comanda vinculada
        vinculo = buscar_vinculo_completo_db(comanda_id)

        if not vinculo:
            return {"ok": False, "message": "Comanda não vinculada"}

        if vinculo['usuario_id'] != usuario_id:
            return {"ok": False, "message": "Comanda não pertence ao usuário"}

        # 4. saldo
        saldo = calcular_saldo_usuario_db(usuario_id)

        if saldo < produto['pontos_necessarios']:
            return {"ok": False, "message": "Pontos insuficientes"}

        # 🔥 AQUI COMEÇA O QUE IMPORTA

        resgate_id = criar_resgate_db(
            conn,
            usuario_id,
            produto_id,
            comanda_id,
            produto['pontos_necessarios']
        )

        debitar_pontos_db(
            conn,
            usuario_id,
            produto['pontos_necessarios'],
            comanda_id
        )

        conn.commit()

        return {
            "ok": True,
            "message": "Resgate realizado com sucesso",
            "resgate_id": resgate_id
        }

    except Exception as e:
        conn.rollback()
        return {"ok": False, "message": f"Erro interno: {str(e)}"}

    finally:
        conn.close()


def listar_resgates_usuario_service(usuario_id):
    resgates = listar_resgates_usuario_db(usuario_id)

    return {
        "ok": True,
        "resgates": resgates
    }