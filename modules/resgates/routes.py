from flask import Blueprint, request, jsonify
from .service import resgatar_produto_service

resgates_bp = Blueprint(
    'resgates',
    __name__,
    url_prefix='/api/resgates'
)

@resgates_bp.route('/resgatar', methods=['POST'])
def resgatar():
    data = request.get_json()

    if not data:
        return jsonify({"ok": False, "message": "Dados inválidos"}), 400

    usuario_id = data.get('usuario_id')
    produto_id = data.get('produto_id')
    comanda_id = data.get('comanda_id')

    if not usuario_id or not produto_id or not comanda_id:
        return jsonify({
            "ok": False,
            "message": "Campos obrigatórios faltando"
        }), 400

    resultado = resgatar_produto_service(
        usuario_id,
        produto_id,
        comanda_id
    )

    return jsonify(resultado)