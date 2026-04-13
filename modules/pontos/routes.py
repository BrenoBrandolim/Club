from flask import Blueprint, request, jsonify
from .service import (
    obter_saldo_usuario_service
)


pontos_bp = Blueprint(
    'pontos',
    __name__,
    url_prefix='/api/pontos'
)

@pontos_bp.route('/saldo/<int:usuario_id>', methods=['GET'])
def obter_saldo(usuario_id):
    resultado = obter_saldo_usuario_service(usuario_id)

    return jsonify(resultado)

