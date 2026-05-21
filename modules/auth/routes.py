"""
modules/auth/routes.py
"""
from flask import Blueprint, request, jsonify
from .service import criar_usuario_service, login_service, buscar_perfil_service
from .decorator import auth_required
from .repository import buscar_usuarios_por_termo_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/usuarios")
CAIXA_API_KEY = "comandas_api_key_qualquer_coisa_longa_e_segura"


@auth_bp.route("/", methods=["POST"])
def criar_usuario():
    data = request.get_json() or {}
    nome     = data.get("nome", "").strip()
    nickname = data.get("nickname", "").strip()
    senha    = data.get("senha", "")

    if not nome or not nickname or not senha:
        return jsonify({"ok": False, "message": "Campos obrigatórios faltando"}), 400

    return jsonify(criar_usuario_service(nome, nickname, senha))


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    nickname = data.get("nickname", "").strip()
    senha    = data.get("senha", "")

    if not nickname or not senha:
        return jsonify({"ok": False, "message": "Campos obrigatórios faltando"}), 400

    return jsonify(login_service(nickname, senha))


@auth_bp.route("/perfil", methods=["GET"])
@auth_required
def perfil(usuario_id_token):
    usuario = buscar_perfil_service(usuario_id_token)
    if not usuario:
        return jsonify({"ok": False, "message": "Usuário não encontrado"}), 404
    return jsonify({"ok": True, "usuario": usuario})


@auth_bp.route("/buscar", methods=["GET"])
def buscar_usuarios():
    if request.headers.get("x-api-key") != CAIXA_API_KEY:
        return jsonify({"ok": False, "message": "Não autorizado"}), 401

    termo = request.args.get("q", "").strip()
    if len(termo) < 2:
        return jsonify({"ok": True, "usuarios": []})

    usuarios = buscar_usuarios_por_termo_db(termo)
    return jsonify({
        "ok": True,
        "usuarios": [
            {
                "id":           u["id"],
                "nome":         u["nome"],
                "nickname":     u["nickname"],
                "saldo_pontos": float(u["saldo_pontos"]),
                "label":        f"{u['nome']} (@{u['nickname']})",
            }
            for u in usuarios
        ],
    })
