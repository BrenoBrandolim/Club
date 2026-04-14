import jwt
from datetime import datetime, timedelta

SECRET_KEY = "qualquer_coisa"  # Tem que melhorar isso depois

def gerar_token(usuario_id):
    payload = {
        "usuario_id": usuario_id,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token


def validar_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["usuario_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None