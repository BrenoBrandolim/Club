"""
modules/resgates/routes.py — CLUB
"""
from flask import Blueprint, request, jsonify
from .service import (
    resgatar_produto_service,
    listar_resgates_service,
    verificar_item_na_comanda_service,
)
from modules.auth.decorator import auth_required

resgates_bp = Blueprint("resgates", __name__, url_prefix="/api/resgates")


@resgates_bp.route("/verificar-item", methods=["GET"])
@auth_required
def verificar_item(usuario_id_token):
    """
    Checa se item já existe na comanda com origem='normal'.
    Query params: numero_comanda, item_id
    """
    numero_comanda = request.args.get("numero_comanda")
    item_id        = request.args.get("item_id")

    if not numero_comanda or not item_id:
        return jsonify({"ok": False, "message": "numero_comanda e item_id obrigatorios"}), 400

    resultado = verificar_item_na_comanda_service(int(numero_comanda), int(item_id))
    return jsonify(resultado)


@resgates_bp.route("/resgatar", methods=["POST"])
@auth_required
def resgatar(usuario_id_token):
    data           = request.get_json() or {}
    produto_id     = data.get("produto_id")
    numero_comanda = data.get("numero_comanda")
    tipo           = data.get("tipo", "local")           # 'local' ou 'viagem'
    substituir     = bool(data.get("substituir", False))
    comanda_item_id= data.get("comanda_item_id")         # id do item pago (substituição)

    if not produto_id or not numero_comanda:
        return jsonify({"ok": False, "message": "produto_id e numero_comanda sao obrigatorios"}), 400

    try:
        resultado = resgatar_produto_service(
            usuario_id      = usuario_id_token,
            produto_id      = int(produto_id),
            numero_comanda  = int(numero_comanda),
            tipo            = tipo,
            substituir      = substituir,
            comanda_item_id = int(comanda_item_id) if comanda_item_id else None,
        )
        return jsonify(resultado)
    except ValueError as e:
        return jsonify({"ok": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "message": "Erro interno ao processar resgate"}), 500


@resgates_bp.route("/usuario", methods=["GET"])
@auth_required
def listar_meus_resgates(usuario_id_token):
    return jsonify(listar_resgates_service(usuario_id_token))
