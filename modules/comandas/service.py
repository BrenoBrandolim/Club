from .repository import (
    verificar_comanda_vinculada_db,
    criar_vinculo_comanda_db,
    buscar_vinculo_completo_db,
    inserir_pontos_db,
    marcar_comanda_processada_db
)

from modules.usuarios.repository import (
    buscar_usuario_por_id
)


def vincular_comanda_usuario_service(comanda_id, usuario_id):


    usuario = buscar_usuario_por_id(usuario_id)

    # Verifica se o usuário existe
    if not usuario:
        return {
            "ok": False,
            "message": "Usuário não encontrado"
        }

    # Verificar se a comanda já está vinculada a um usuário
    if verificar_comanda_vinculada_db(comanda_id):
        return {
            "ok": False,
            "message": "Comanda já vinculada a um usuário"
        }
    

    # Criar o vínculo entre a comanda e o usuário
    vinculo_id = criar_vinculo_comanda_db(comanda_id, usuario_id)

    return {
        "ok": True,
        "message": "Comanda vinculada ao usuário com sucesso",
        "vinculo_id": vinculo_id

    }

def comanda_fechada_service(comanda_id, lucro_liquido):

    # Verifica se a comanda esta vinculada a um usuário
    vinculo = buscar_vinculo_completo_db(comanda_id)

    # Se não estiver vinculada, retorna erro
    if not vinculo:
        return {
            "ok": False,
            "message": "Comanda não vinculada a um usuário"
        }

    #Se já estiver processada, retorna erro
    if vinculo['processada']:
        return {
            "ok": False,
            "message": "Comanda já processada"
        }
    
    if lucro_liquido <= 0:
        return {
            "ok": False,
            "message": "Comanda sem lucro, não gera pontos"
        }

    # Calcular pontos
    pontos = lucro_liquido / 10

    # Inserindo pontos para o usuário
    inserir_pontos_db(
        usuario_id=vinculo['usuario_id'], #Puxa o id que buscamos com função buscar vinculo id que está relavionada a "vinculo"
        valor=pontos,
        comanda_id=comanda_id
    )
    
    marcar_comanda_processada_db(comanda_id)
    
    return {
        "ok": True,
        "message": "Comanda processada e pontos inseridos com sucesso",
        "pontos": pontos
    }
