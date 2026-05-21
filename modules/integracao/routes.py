"""
modules/integracao/routes.py — CLUB
Recebe evento do Caixa: comanda fechada → credita pontos.

CORREÇÃO: pontos = lucro / 10  (float, sem arredondamento)
Exemplos: R$2,50 lucro → 0.25 pts | R$5 → 0.5 pts | R$10 → 1.0 pts
"""
from flask import Blueprint, request, jsonify
from modules.pontos.repository import buscar_usuario_por_comanda_db, registrar_pontos_db

integracao_bp = Blueprint("integracao", __name__, url_prefix="/api/comandas")
CAIXA_API_KEY = "comandas_api_key_qualquer_coisa_longa_e_segura"


@integracao_bp.route("/fechada", methods=["POST"])
def comanda_fechada():
    if request.headers.get("x-api-key") != CAIXA_API_KEY:
        return jsonify({"ok": False, "message": "Nao autorizado"}), 401

    data       = request.get_json() or {}
    comanda_id = data.get("comanda_id")
    lucro      = float(data.get("lucro_liquido", 0))

    if not comanda_id:
        return jsonify({"ok": False, "message": "comanda_id obrigatorio"}), 400

    # CORREÇÃO: float sem arredondamento
    pontos = lucro / 10

    if pontos <= 0:
        return jsonify({"ok": True, "message": "Lucro insuficiente para gerar pontos."})

    vinculo = buscar_usuario_por_comanda_db(comanda_id)
    if not vinculo:
        return jsonify({"ok": True, "message": "Comanda sem usuario vinculado."})

    usuario_id = vinculo["usuario_id"]
    registrar_pontos_db(
        usuario_id = usuario_id,
        tipo       = "ganho",
        valor      = pontos,   # float
        comanda_id = comanda_id,
        descricao  = f"Comanda #{comanda_id} — R$ {lucro:.2f} lucro → {pontos:.4f} pts",
    )

    return jsonify({
        "ok":     True,
        "pontos": pontos,
        "message": f"{pontos:.4f} pontos creditados ao usuario {usuario_id}.",
    })
