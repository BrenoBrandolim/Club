"""
modules/auth/decorator.py
"""
from functools import wraps
from flask import request, jsonify
from .jwt_handler import validar_token


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({"ok": False, "message": "Token não enviado"}), 401

        usuario_id = validar_token(token)
        if not usuario_id:
            return jsonify({"ok": False, "message": "Token inválido ou expirado"}), 401

        kwargs["usuario_id_token"] = usuario_id
        return f(*args, **kwargs)
    return decorated
