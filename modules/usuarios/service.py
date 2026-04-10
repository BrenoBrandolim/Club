import bcrypt
from .repository import (
    criar_usuario,
    buscar_por_nickname
)

def criar_usuario_service(nome, nickname, senha):

    # Verificar se nickname já existee
    if buscar_por_nickname(nickname):
        return {
            "ok": False,
            "message": "Nickname já existe"
        }
    
    # Gerar hash da senha
    senha_hash = bcrypt.hashpw(
        senha.encode('utf-8'),
        bcrypt.gensalt()
    )

    # Enviar para o banco
    user_id = criar_usuario(nome, nickname, senha_hash)

    return {
        "ok": True,
        "message": "Usuário criado com sucesso",
        "user_id": user_id
    }
    