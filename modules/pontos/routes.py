from flask import Blueprint, request, jsonify

from modules.auth.decorator import auth_required
from .service import (
    obter_saldo_usuario_service
)


pontos_bp = Blueprint(
    'pontos',
    __name__,
    url_prefix='/api/pontos'
)

@pontos_bp.route('/saldo', methods=['GET'])
@auth_required
def obter_saldo(usuario_id_token):
    resultado = obter_saldo_usuario_service(usuario_id_token)

    return jsonify(resultado)

