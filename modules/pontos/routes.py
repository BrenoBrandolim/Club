"""modules/pontos/routes.py"""
from flask import Blueprint, request, jsonify
from .service import saldo_service, historico_service
from .repository import buscar_ranking_db
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

@pontos_bp.route("/ranking", methods=["GET"])
def ranking():
    """Top 10 por pontos ganhos totais. Público (sem auth) para o placar."""
    rows = buscar_ranking_db(10)
    return jsonify({
        "ok":    True,
        "ranking": [
            {
                "posicao":       i + 1,
                "nome":          r["nome"],
                "nickname":      r["nickname"],
                "pontos_ganhos": float(r["pontos_ganhos"]),
            }
            for i, r in enumerate(rows)
        ],
    })