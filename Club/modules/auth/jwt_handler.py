"""
modules/auth/jwt_handler.py
"""
import jwt
import os
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET", "club_jwt_secret_troque_em_producao")


def gerar_token(usuario_id: int) -> str:
    payload = {
        "usuario_id": usuario_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def validar_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["usuario_id"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
