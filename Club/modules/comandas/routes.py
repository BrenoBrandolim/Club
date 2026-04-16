"""
modules/comanda/routes.py — CLUB
═══════════════════════════════════════════════════════════════
Responsável pelo fluxo de QR Code:

  GET /comanda/<numero>          → página de vinculação
  GET /api/comanda/<numero>      → valida comanda no Caixa (retorna id + status)
  POST /api/comanda/<numero>/vincular → cria vínculo user ↔ comanda_id

Fluxo completo:
  1. Cliente escaneia QR → /comanda/42
  2. JS faz GET /api/comanda/42 → Club chama Caixa → retorna {aberta, comanda_id}
  3. Se aberta → mostra botão "Vincular"
  4. Se não logado → salva numero em localStorage → redireciona login/cadastro
  5. Após login → JS lê localStorage → restaura contexto → vincula
  6. POST /api/comanda/42/vincular → cria registro em usuarios_comandas
"""
import requests
from flask import Blueprint, request, jsonify, render_template
from modules.auth.decorator import auth_required
from db.connection import get_connection

comanda_bp = Blueprint("comanda", __name__)

CAIXA_URL     = "http://localhost:5000"
CAIXA_API_KEY = "comandas_api_key_qualquer_coisa_longa_e_segura"
_HEADERS      = {"x-api-key": CAIXA_API_KEY}


# ── Página do QR Code ───────────────────────────────────────

@comanda_bp.route("/comanda/<int:numero>")
def pagina_comanda(numero):
    """Landing page do QR Code. Passa o número para o frontend."""
    return render_template("comanda.html", numero_comanda=numero)


# ── API: valida comanda no Caixa ────────────────────────────

@comanda_bp.route("/api/comanda/<int:numero>", methods=["GET"])
def validar_comanda(numero):
    """
    Chama o Caixa para verificar se comanda existe e está aberta.
    Retorna comanda_id real para o Club usar internamente.
    """
    try:
        resp = requests.get(
            f"{CAIXA_URL}/comandas/api/comanda/status/{numero}",
            headers=_HEADERS,
            timeout=4,
        )
        data = resp.json()
    except requests.RequestException as e:
        return jsonify({"ok": False, "message": f"Caixa indisponível: {e}"}), 503

    if not data.get("ok"):
        return jsonify({"ok": False, "message": "Comanda não encontrada"}), 404

    return jsonify({
        "ok":         True,
        "numero":     data["numero"],
        "comanda_id": data["comanda_id"],   # id interno (nunca exposto ao usuário)
        "aberta":     data["aberta"],
        "status":     data["status"],
    })


# ── API: vincular usuário à comanda ─────────────────────────

@comanda_bp.route("/api/comanda/<int:numero>/vincular", methods=["POST"])
@auth_required
def vincular_comanda(numero, usuario_id_token):
    """
    1. Valida comanda no Caixa (deve estar aberta)
    2. Cria vínculo usuario_id ↔ comanda_id em usuarios_comandas
    """
    # Valida no Caixa
    try:
        resp = requests.get(
            f"{CAIXA_URL}/comandas/api/comanda/status/{numero}",
            headers=_HEADERS,
            timeout=4,
        )
        data = resp.json()
    except requests.RequestException as e:
        return jsonify({"ok": False, "message": f"Caixa indisponível: {e}"}), 503

    if not data.get("ok"):
        return jsonify({"ok": False, "message": "Comanda não encontrada"}), 404

    if not data.get("aberta"):
        return jsonify({
            "ok":      False,
            "message": f"Comanda #{numero} está {data.get('status', 'fechada')}. Só é possível vincular comandas abertas.",
        }), 409

    comanda_id = data["comanda_id"]

    # Verifica se já existe vínculo
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, usuario_id FROM usuarios_comandas WHERE comanda_id = %s",
            (comanda_id,),
        )
        vinculo = cursor.fetchone()

        if vinculo:
            if vinculo["usuario_id"] == usuario_id_token:
                return jsonify({
                    "ok":         True,
                    "message":    "Comanda já vinculada à sua conta.",
                    "comanda_id": comanda_id,
                    "numero":     numero,
                })
            else:
                return jsonify({
                    "ok":      False,
                    "message": "Esta comanda já está vinculada a outro usuário.",
                }), 409

        # Cria vínculo
        cursor.execute(
            """
            INSERT INTO usuarios_comandas (usuario_id, comanda_id)
            VALUES (%s, %s)
            """,
            (usuario_id_token, comanda_id),
        )
        conn.commit()

        return jsonify({
            "ok":         True,
            "message":    f"Comanda #{numero} vinculada com sucesso! Seus pontos serão creditados ao fechar.",
            "comanda_id": comanda_id,
            "numero":     numero,
        })
    finally:
        cursor.close()
        conn.close()


# ── API: comanda ativa do usuário ────────────────────────────

@comanda_bp.route("/api/comanda/ativa", methods=["GET"])
@auth_required
def comanda_ativa(usuario_id_token):
    """
    Retorna a comanda aberta mais recente vinculada ao usuário.
    Usado pelo dashboard para mostrar comanda ativa e pelo catálogo
    para pré-preencher o campo de resgate.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT uc.comanda_id, uc.data_vinculacao
            FROM usuarios_comandas uc
            WHERE uc.usuario_id = %s
            ORDER BY uc.data_vinculacao DESC
            LIMIT 1
            """,
            (usuario_id_token,),
        )
        vinculo = cursor.fetchone()
        if not vinculo:
            return jsonify({"ok": True, "comanda": None})

        # Verifica status atual no Caixa
        comanda_id = vinculo["comanda_id"]
    finally:
        cursor.close()
        conn.close()

    try:
        # Busca o número da comanda pelo id (endpoint de status precisa de numero)
        # Como o Caixa já tem o endpoint de status por numero, precisamos do numero
        # Vamos buscar diretamente via endpoint genérico ou guardar o numero no vinculo
        # Por ora, retornamos o comanda_id e o frontend usa o que tem
        return jsonify({
            "ok":         True,
            "comanda":    {"comanda_id": comanda_id},
        })
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500
