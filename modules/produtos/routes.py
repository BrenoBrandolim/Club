from flask import Blueprint, jsonify
from .service import listar_produtos_service

produtos_bp = Blueprint(
    'produtos',
    __name__,
    url_prefix='/api/produtos'
)

@produtos_bp.route('/', methods=['GET'])
def listar_produtos():
    return jsonify(listar_produtos_service())
