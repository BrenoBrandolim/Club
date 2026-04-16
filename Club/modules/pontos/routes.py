"""
modules/pontos/routes.py
"""
from flask import Blueprint, request, jsonify
from .service import saldo_service, historico_service, vincular_comanda_service
from modules.auth.decorator import auth_required

pontos_bp = Blueprint("pontos", __name__, url_prefix="/api/pontos")


@pontos_bp.route("/saldo", methods=["GET"])
@auth_required
def saldo(usuario_id_token):
    return jsonify(saldo_service(usuario_id_token))


@pontos_bp.route("/historico", methods=["GET"])
@auth_required
def historico(usuario_id_token):
    return jsonify(historico_service(usuario_id_token))


@pontos_bp.route("/vincular-comanda", methods=["POST"])
@auth_required
def vincular_comanda(usuario_id_token):
    data = request.get_json() or {}
    comanda_id = data.get("comanda_id")
    if not comanda_id:
        return jsonify({"ok": False, "message": "comanda_id obrigatório"}), 400
    return jsonify(vincular_comanda_service(usuario_id_token, int(comanda_id)))
