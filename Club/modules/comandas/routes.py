"""
modules/comanda/routes.py — CLUB
BUG FIX: comparação por comanda_id (interno) e não por numero_comanda.
Antes: verificava se qualquer comanda com o NÚMERO está aberta.
Agora: verifica se a comanda com o MESMO ID INTERNO ainda está aberta.
Isso resolve o caso de comanda #10 fechada + nova #10 aberta — o usuário
não fica mais preso, pois os IDs internos são diferentes.
"""
import requests
from flask import Blueprint, request, jsonify, render_template
from modules.auth.decorator import auth_required
from db.connection import get_connection

comanda_bp = Blueprint("comanda", __name__)

CAIXA_URL     = "http://localhost:5000"
CAIXA_API_KEY = "comandas_api_key_qualquer_coisa_longa_e_segura"
_HEADERS      = {"x-api-key": CAIXA_API_KEY}


@comanda_bp.route("/comanda/<int:numero>")
def pagina_comanda(numero):
    return render_template("comanda.html", numero_comanda=numero)


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


@comanda_bp.route("/api/comanda/<int:numero>/vincular", methods=["POST"])
@auth_required
def vincular_comanda(numero, usuario_id_token):
    """
    BUG FIX: ao verificar se o usuário já tem comanda ativa, compara
    o comanda_id retornado pelo Caixa com o comanda_id armazenado
    no vínculo. Se forem diferentes, é outra instância da comanda
    (mesmo número, mas abertura diferente) — o vínculo anterior
    está extinto e o usuário pode vincular a nova.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
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
        try:
            resp = requests.get(
                f"{CAIXA_URL}/comandas/api/comanda/status/{vinculo_existente['numero_comanda']}",
                headers=_HEADERS, timeout=4,
            )
            data_ant = resp.json()
            # FIX: só bloqueia se for EXATAMENTE o mesmo comanda_id interno
            # Se o Caixa retornou um ID diferente, a comanda antiga foi fechada
            # e uma nova com o mesmo número foi aberta — vínculo anterior é inválido.
            if (data_ant.get("ok") and data_ant.get("aberta")
                    and data_ant.get("comanda_id") == vinculo_existente["comanda_id"]):
                return jsonify({
                    "ok":      False,
                    "message": f"Você já tem a comanda #{vinculo_existente['numero_comanda']} aberta vinculada. Finalize-a antes de vincular outra.",
                }), 409
        except Exception:
            pass  # Se Caixa offline, permite continuar

    # Valida a nova comanda
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

    # Verifica se esta comanda já está vinculada a outro usuário
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


@comanda_bp.route("/api/comanda/ativa", methods=["GET"])
@auth_required
def comanda_ativa(usuario_id_token):
    """
    Retorna a comanda ativa do usuário.
    BUG FIX: compara o comanda_id retornado pelo Caixa com o armazenado.
    Se diferente, significa que o número foi reutilizado e a comanda
    original do usuário foi fechada — retorna None corretamente.
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

    try:
        resp = requests.get(
            f"{CAIXA_URL}/comandas/api/comanda/status/{numero}",
            headers=_HEADERS, timeout=4,
        )
        data = resp.json()

        # FIX: só considera ativa se o comanda_id bater exatamente
        if (data.get("ok") and data.get("aberta")
                and data.get("comanda_id") == vinculo["comanda_id"]):
            return jsonify({
                "ok":     True,
                "comanda": {
                    "numero":     numero,
                    "comanda_id": data["comanda_id"],
                },
            })
        else:
            # Comanda fechada ou reutilizada — sem ativa
            return jsonify({"ok": True, "comanda": None})

    except Exception:
        # Caixa offline — retorna o que temos com aviso
        return jsonify({
            "ok":     True,
            "comanda": {
                "numero":     numero,
                "comanda_id": vinculo["comanda_id"],
            },
            "aviso": "Status não verificado (Caixa offline)",
        })
