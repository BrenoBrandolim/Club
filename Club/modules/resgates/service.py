"""
modules/resgates/service.py — CLUB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CORREÇÕES:
1. Comanda sempre a mais recente ABERTA (Caixa corrigido)
2. Pontos float sem arredondamento (lucro/10)
3. Substituição de item pago por resgate
4. verificar_item_na_comanda_service para pré-checagem
"""

import requests
from modules.pontos.repository   import buscar_saldo_db
from modules.pontos.service      import debitar_pontos_service
from modules.produtos.repository import buscar_produto_por_id_db
from .repository import registrar_resgate_db, listar_resgates_usuario_db

CAIXA_URL     = "http://localhost:5000"
CAIXA_API_KEY = "comandas_api_key_qualquer_coisa_longa_e_segura"
_HEADERS      = {"x-api-key": CAIXA_API_KEY}


def _validar_comanda_caixa(numero_comanda: int) -> dict:
    """Retorna comanda ABERTA mais recente com esse número."""
    try:
        resp = requests.get(
            f"{CAIXA_URL}/comandas/api/comanda/status/{numero_comanda}",
            headers=_HEADERS, timeout=4,
        )
        data = resp.json()
    except requests.RequestException as e:
        raise ValueError(f"Caixa indisponivel: {e}")

    if not data.get("ok"):
        raise ValueError(f"Comanda #{numero_comanda} nao encontrada ou nao esta aberta.")
    if not data.get("aberta"):
        raise ValueError(
            f"Comanda #{numero_comanda} esta {data.get('status','fechada')}. "
            "Abra uma nova comanda para resgatar."
        )
    return data


def verificar_item_na_comanda_service(numero_comanda: int, item_id: int) -> dict:
    """
    Checa se item ja existe na comanda com origem='normal'.
    Frontend usa isso para oferecer substituicao antes do resgate.
    """
    try:
        caixa_data = _validar_comanda_caixa(numero_comanda)
        resp = requests.get(
            f"{CAIXA_URL}/comandas/api/comanda/{numero_comanda}/tem-item/{item_id}",
            headers=_HEADERS, timeout=4,
        )
        data = resp.json()
        return {
            "ok":              True,
            "tem_item":        data.get("tem_item", False),
            "comanda_item_id": data.get("comanda_item_id"),
            "comanda_aberta":  caixa_data.get("aberta", False),
        }
    except ValueError as e:
        return {"ok": False, "message": str(e), "tem_item": False}
    except Exception:
        return {"ok": True, "tem_item": False, "comanda_item_id": None}


def resgatar_produto_service(
    usuario_id:      int,
    produto_id:      int,
    numero_comanda:  int,
    tipo:            str  = "local",
    substituir:      bool = False,
    comanda_item_id: int | None = None,
) -> dict:
    # 1. Produto
    produto = buscar_produto_por_id_db(produto_id)
    if not produto or not produto["ativo"]:
        raise ValueError("Produto nao disponivel para resgate.")

    pontos_necessarios = float(produto["pontos_necessarios"])

    # 2. Saldo (float, sem arredondamento)
    saldo = buscar_saldo_db(usuario_id)
    if saldo < pontos_necessarios:
        raise ValueError(
            f"Pontos insuficientes. Saldo: {saldo:.2f} pts | "
            f"Necessario: {pontos_necessarios:.2f} pts."
        )

    # 3. Comanda — sempre a mais recente aberta
    caixa_data = _validar_comanda_caixa(numero_comanda)
    comanda_id_interno = caixa_data["comanda_id"]

    # 4/5. Substituição ou adição simples
    if substituir and comanda_item_id:
        try:
            resp = requests.post(
                f"{CAIXA_URL}/comandas/api/comanda/substituir-item",
                json={
                    "numero_comanda":  numero_comanda,
                    "item_id":         produto["item_id"],
                    "comanda_item_id": comanda_item_id,
                },
                headers=_HEADERS, timeout=4,
            )
            if not resp.ok:
                msg = resp.json().get("message", "Erro ao substituir")
                raise ValueError(f"Caixa rejeitou substituicao: {msg}")
        except requests.RequestException as e:
            raise ValueError(f"Erro de conexao com o Caixa: {e}")
    else:
        try:
            resp = requests.post(
                f"{CAIXA_URL}/comandas/adicionar-item-clube",
                json={"numero_comanda": numero_comanda, "item_id": produto["item_id"]},
                headers=_HEADERS, timeout=4,
            )
            if not resp.ok:
                msg = resp.json().get("message", "Erro desconhecido")
                raise ValueError(f"Caixa rejeitou resgate: {msg}")
        except requests.RequestException as e:
            raise ValueError(f"Erro de conexao com o Caixa: {e}")

    # 6. Debita pontos (float)
    descricao = f"Resgate: {produto['nome']} ({tipo})" + (" [substituicao]" if substituir else "")
    debitar_pontos_service(usuario_id, pontos_necessarios, comanda_id_interno, descricao)

    # 7. Registra
    registrar_resgate_db(usuario_id, produto_id, comanda_id_interno, pontos_necessarios, tipo)

    acao = "substituido" if substituir else "adicionado"
    return {"ok": True, "message": f"{produto['nome']} {acao} na comanda #{numero_comanda}!"}


def listar_resgates_service(usuario_id: int) -> dict:
    resgates = listar_resgates_usuario_db(usuario_id)
    return {
        "ok": True,
        "resgates": [
            {**r, "pontos_gastos": float(r["pontos_gastos"]), "data_criacao": str(r["data_criacao"])}
            for r in resgates
        ],
    }
