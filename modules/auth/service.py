"""
modules/auth/service.py
"""
import bcrypt
from .repository import criar_usuario_db, buscar_por_nickname_db, buscar_usuario_por_id_db
from .jwt_handler import gerar_token


def criar_usuario_service(nome: str, nickname: str, senha: str) -> dict:
    if buscar_por_nickname_db(nickname):
        return {"ok": False, "message": "Nickname já existe"}

    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    user_id = criar_usuario_db(nome, nickname, senha_hash)
    token = gerar_token(user_id)
    return {"ok": True, "message": "Usuário criado", "token": token, "user_id": user_id}


def login_service(nickname: str, senha: str) -> dict:
    usuario = buscar_por_nickname_db(nickname)
    if not usuario:
        return {"ok": False, "message": "Nickname ou senha incorretos"}

    if not bcrypt.checkpw(senha.encode(), usuario["senha_hash"].encode()):
        return {"ok": False, "message": "Nickname ou senha incorretos"}

    token = gerar_token(usuario["id"])
    return {
        "ok": True,
        "message": "Login bem-sucedido",
        "token": token,
        "nome": usuario["nome"],
        "nickname": usuario["nickname"],
    }


def buscar_perfil_service(usuario_id: int) -> dict | None:
    return buscar_usuario_por_id_db(usuario_id)
