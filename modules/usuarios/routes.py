from flask import Blueprint, request, jsonify
from .service import criar_usuario_service

usuario_bp = Blueprint(
    'usuarios',
    __name__,
    url_prefix='/api/usuarios'
)

@usuario_bp.route('/', methods=['POST'])
def criar_usuario():
    data = request.get_json()

    nome = data.get('nome')
    nickname = data.get('nickname')
    senha = data.get('senha')

    if not nome or not nickname or not senha:
        return jsonify({
            "ok": False,
            "mensagem": "Campos obrigatórios faltando"
        }), 400
    
    resultado = criar_usuario_service(nome, nickname, senha)

    return jsonify(resultado)
