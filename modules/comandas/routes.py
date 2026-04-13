from flask import Blueprint, request, jsonify

from .service import (
    vincular_comanda_usuario_service,
    comanda_fechada_service
)


comandas_bp = Blueprint(
    'comandas',
    __name__,
    url_prefix='/api/comandas'
)

@comandas_bp.route('/vincular', methods=['POST'])
def vincular_comanda_usuario():
    data = request.get_json()

    if not data:
        return jsonify({
            "ok": False,
            "message": "Dados de entrada inválidos"
        }), 400

    comanda_id = data.get('comanda_id')
    usuario_id = data.get('usuario_id')

    if not comanda_id or not usuario_id:
        return jsonify({
            "ok": False,
            "message": "Campos obrigatórios faltando"
        }), 400
    
    resultado = vincular_comanda_usuario_service(comanda_id, usuario_id)

    return jsonify(resultado)


@comandas_bp.route('/fechada', methods=['POST'])
def comanda_fechada():
    data = request.get_json()

    if not data:
        return jsonify({
            "ok": False,
            "message": "Dados de entrada inválidos"
        }), 400
    
    comanda_id = data.get('comanda_id')
    lucro_liquido = data.get('lucro_liquido')

    if not comanda_id or lucro_liquido is None:
        return jsonify({
            "ok": False,
            "message": "Campos obrigatórios faltando"
        }), 400
    
    resultado = comanda_fechada_service(comanda_id, lucro_liquido)

    return jsonify(resultado)

