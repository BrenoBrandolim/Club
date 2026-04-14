import bcrypt

from .repository import (
    criar_usuario,
    buscar_por_nickname
)

from modules.auth.jwt_handler import (
    gerar_token
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
    

def login_usuario_service(nickname, senha):
    
    # Verificar se o usuário existe
    usuario = buscar_por_nickname(nickname)

    if not usuario:
        return {
            "ok": False,
            "message": "Nickname ou senha incorretos"
        }
    
    # Verificar a senha
    if not bcrypt.checkpw(senha.encode('utf-8'), usuario['senha_hash'].encode('utf-8')):
        return {
            "ok": False,
            "message": "Nickname ou senha incorretos"
        }
    
    token = gerar_token(usuario['id'])
    
    return {
        "ok": True,
        "message": "Login bem-sucedido",
        "token": token
    }