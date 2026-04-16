"""
modules/auth/routes.py
"""
from flask import Blueprint, request, jsonify
from .service import criar_usuario_service, login_service, buscar_perfil_service
from .decorator import auth_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/usuarios")


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
