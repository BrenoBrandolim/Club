from flask import Blueprint, request, jsonify

from modules.auth.decorator import (
    auth_required
)

from .service import (
    resgatar_produto_service,
    listar_resgates_usuario_service
)


resgates_bp = Blueprint(
    'resgates',
    __name__,
    url_prefix='/api/resgates'
)

@resgates_bp.route('/resgatar', methods=['POST'])
@auth_required
def resgatar(usuario_id_token):
    data = request.get_json()

    if not data:
        return jsonify({"ok": False, "message": "Dados inválidos"}), 400

    produto_id = data.get('produto_id')
    comanda_id = data.get('comanda_id')

    if not produto_id or not comanda_id:
        return jsonify({
            "ok": False,
            "message": "Campos obrigatórios faltando"
        }), 400

    resultado = resgatar_produto_service(
        usuario_id_token,
        produto_id,
        comanda_id
    )

    return jsonify(resultado)

@resgates_bp.route('/usuario', methods=['GET'])
@auth_required
def listar_resgates(usuario_id_token):
    return jsonify(listar_resgates_usuario_service(usuario_id_token))