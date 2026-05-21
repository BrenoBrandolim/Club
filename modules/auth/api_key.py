import os
from flask import request, jsonify
from functools import wraps

API_KEY = os.getenv("API_KEY")
print("API_KEY carregada:", API_KEY)
def api_key_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        key = request.headers.get("x-api-key")

        if key != API_KEY:
            return jsonify({
                "ok": False,
                "message": "Acesso não autorizado"
            }), 403

        return f(*args, **kwargs)
    
    return wrapper