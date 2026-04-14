from flask import Blueprint, jsonify, request
from .service import (
    listar_produtos_service,
    sync_produto_service
)

produtos_bp = Blueprint(
    'produtos',
    __name__,
    url_prefix='/api/produtos'
)

@produtos_bp.route('/', methods=['GET'])
def listar_produtos():
    return jsonify(listar_produtos_service())

@produtos_bp.route('/sync', methods=['POST'])
def sync_produto():
    data = request.json

    sync_produto_service(data)

    return {"ok": True}