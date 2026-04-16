"""
modules/produtos/routes.py
"""
from flask import Blueprint, request, jsonify
from .service import listar_produtos_service, buscar_produto_service, sincronizar_produto_service, editar_produto_service
from modules.auth.decorator import auth_required

produtos_bp = Blueprint("produtos", __name__, url_prefix="/api/produtos")

# Chave que o Caixa usa para autenticar chamadas de sincronização
CAIXA_API_KEY = "comandas_api_key_qualquer_coisa_longa_e_segura"


def _verificar_api_key():
    return request.headers.get("x-api-key") == CAIXA_API_KEY


@produtos_bp.route("/", methods=["GET"])
def listar_produtos():
    """Público — catálogo para a UI."""
    produtos = listar_produtos_service()
    return jsonify({"ok": True, "produtos": [
        {**p, "pontos_necessarios": float(p["pontos_necessarios"]),
         "preco_dinheiro": float(p["preco_dinheiro"] or 0)}
        for p in produtos
    ]})


@produtos_bp.route("/<int:produto_id>", methods=["GET"])
def detalhe_produto(produto_id):
    p = buscar_produto_service(produto_id)
    if not p:
        return jsonify({"ok": False, "message": "Produto não encontrado"}), 404
    return jsonify({"ok": True, "produto": p})


@produtos_bp.route("/sync", methods=["POST"])
def sincronizar():
    """Recebe produto sincronizado pelo Caixa."""
    if not _verificar_api_key():
        return jsonify({"ok": False, "message": "Não autorizado"}), 401

    data = request.get_json() or {}
    sincronizar_produto_service(
        item_id      = data.get("item_id"),
        nome         = data.get("nome"),
        pontos       = data.get("pontos", 0),
        preco_dinheiro = data.get("preco_dinheiro", 0),
        foto_url     = data.get("foto_url", ""),
    )
    return jsonify({"ok": True})


@produtos_bp.route("/<int:produto_id>", methods=["PUT"])
@auth_required
def editar_produto(produto_id, usuario_id_token):
    data = request.get_json() or {}
    editar_produto_service(
        produto_id = produto_id,
        nome       = data.get("nome"),
        foto_url   = data.get("foto_url", ""),
        pontos     = data.get("pontos", 0),
        ativo      = data.get("ativo", True),
    )
    return jsonify({"ok": True, "message": "Produto atualizado"})
