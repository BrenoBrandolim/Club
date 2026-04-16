"""modules/comanda/routes.py — CLUB
Fluxo QR Code. Ajustes:
  - vincular: 1 comanda ativa por usuário (rejeita se ainda tiver aberta)
  - vincular: salva numero_comanda para exibição sem chamar Caixa
  - comanda_ativa: retorna numero real + verifica se ainda aberta no Caixa
"""
import requests
from flask import Blueprint, request, jsonify, render_template
from modules.auth.decorator import auth_required
from db.connection import get_connection

comanda_bp = Blueprint("comanda", __name__)

CAIXA_URL     = "http://localhost:5000"
CAIXA_API_KEY = "comandas_api_key_qualquer_coisa_longa_e_segura"
_HEADERS      = {"x-api-key": CAIXA_API_KEY}

# ── Página QR ──────────────────────────────────────────────
@comanda_bp.route("/comanda/<int:numero>")
def pagina_comanda(numero):
    return render_template("comanda.html", numero_comanda=numero)

# ── API: valida comanda no Caixa ───────────────────────────
@comanda_bp.route("/api/comanda/<int:numero>", methods=["GET"])
def validar_comanda(numero):
    try:
        resp = requests.get(
            f"{CAIXA_URL}/comandas/api/comanda/status/{numero}",
            headers=_HEADERS, timeout=4,
        )
        data = resp.json()
    except requests.RequestException as e:
        return jsonify({"ok": False, "message": f"Caixa indisponível: {e}"}), 503
    if not data.get("ok"):
        return jsonify({"ok": False, "message": "Comanda não encontrada"}), 404
    return jsonify({
        "ok":         True,
        "numero":     data["numero"],
        "comanda_id": data["comanda_id"],
        "aberta":     data["aberta"],
        "status":     data["status"],
    })

# ── API: vincular ──────────────────────────────────────────
@comanda_bp.route("/api/comanda/<int:numero>/vincular", methods=["POST"])
@auth_required
def vincular_comanda(numero, usuario_id_token):
    """
    Regras:
    1. Usuário pode ter só 1 comanda ativa por vez.
    2. Antes de vincular nova, verifica se a mais recente ainda está aberta.
    3. Se aberta → rejeita. Se fechada/não existe → permite.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verifica se usuário já tem vínculo ativo
        cursor.execute(
            """
            SELECT comanda_id, numero_comanda
            FROM usuarios_comandas
            WHERE usuario_id = %s
            ORDER BY data_vinculacao DESC
            LIMIT 1
            """,
            (usuario_id_token,),
        )
        vinculo_existente = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if vinculo_existente and vinculo_existente.get("numero_comanda"):
        # Verifica no Caixa se a comanda anterior ainda está aberta
        try:
            resp = requests.get(
                f"{CAIXA_URL}/comandas/api/comanda/status/{vinculo_existente['numero_comanda']}",
                headers=_HEADERS, timeout=4,
            )
            data_ant = resp.json()
            if data_ant.get("ok") and data_ant.get("aberta"):
                return jsonify({
                    "ok":      False,
                    "message": f"Você já tem a comanda #{vinculo_existente['numero_comanda']} vinculada e aberta. Finalize-a antes de vincular outra.",
                }), 409
        except Exception:
            pass  # Se Caixa indisponível, permite continuar

    # Valida nova comanda no Caixa
    try:
        resp = requests.get(
            f"{CAIXA_URL}/comandas/api/comanda/status/{numero}",
            headers=_HEADERS, timeout=4,
        )
        data = resp.json()
    except requests.RequestException as e:
        return jsonify({"ok": False, "message": f"Caixa indisponível: {e}"}), 503

    if not data.get("ok"):
        return jsonify({"ok": False, "message": "Comanda não encontrada"}), 404
    if not data.get("aberta"):
        return jsonify({
            "ok":      False,
            "message": f"Comanda #{numero} está {data.get('status','fechada')}.",
        }), 409

    comanda_id = data["comanda_id"]

    # Verifica se esta comanda específica já está vinculada a outro usuário
    conn2 = get_connection()
    cursor2 = conn2.cursor(dictionary=True)
    try:
        cursor2.execute(
            "SELECT id, usuario_id FROM usuarios_comandas WHERE comanda_id = %s",
            (comanda_id,),
        )
        vinculo_comanda = cursor2.fetchone()
        if vinculo_comanda:
            if vinculo_comanda["usuario_id"] == usuario_id_token:
                return jsonify({
                    "ok":      True,
                    "message": "Comanda já vinculada à sua conta.",
                    "numero":  numero,
                })
            else:
                return jsonify({
                    "ok":      False,
                    "message": "Esta comanda já está vinculada a outro usuário.",
                }), 409

        # Cria vínculo com numero_comanda para evitar chamar Caixa depois
        cursor2.execute(
            """
            INSERT INTO usuarios_comandas (usuario_id, comanda_id, numero_comanda)
            VALUES (%s, %s, %s)
            """,
            (usuario_id_token, comanda_id, numero),
        )
        conn2.commit()
        return jsonify({
            "ok":      True,
            "message": f"Comanda #{numero} vinculada! Seus pontos serão creditados ao fechar.",
            "numero":  numero,
        })
    finally:
        cursor2.close()
        conn2.close()

# ── API: comanda ativa do usuário ──────────────────────────
@comanda_bp.route("/api/comanda/ativa", methods=["GET"])
@auth_required
def comanda_ativa(usuario_id_token):
    """
    Retorna comanda ativa do usuário.
    Verifica no Caixa se ainda está aberta (pode ter sido fechada).
    Se fechada → retorna comanda: None (sumiu automaticamente).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT comanda_id, numero_comanda, data_vinculacao
            FROM usuarios_comandas
            WHERE usuario_id = %s
            ORDER BY data_vinculacao DESC
            LIMIT 1
            """,
            (usuario_id_token,),
        )
        vinculo = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not vinculo or not vinculo.get("numero_comanda"):
        return jsonify({"ok": True, "comanda": None})

    numero = vinculo["numero_comanda"]

    # Verifica status atual no Caixa
    try:
        resp = requests.get(
            f"{CAIXA_URL}/comandas/api/comanda/status/{numero}",
            headers=_HEADERS, timeout=4,
        )
        data = resp.json()
        if data.get("ok") and data.get("aberta"):
            return jsonify({
                "ok":     True,
                "comanda": {"numero": numero, "comanda_id": data["comanda_id"]},
            })
        else:
            # Fechada ou não encontrada → sem comanda ativa
            return jsonify({"ok": True, "comanda": None})
    except Exception:
        # Se Caixa offline, mostra o que temos mas avisa
        return jsonify({
            "ok":     True,
            "comanda": {"numero": numero, "comanda_id": vinculo["comanda_id"]},
            "aviso":  "Status não verificado (Caixa offline)",
        })