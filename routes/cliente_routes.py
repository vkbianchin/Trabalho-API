"""
Camada ROUTE (API).

Responsável só pelo HTTP: receber a requisição, repassar para o
controller e devolver a resposta em JSON. Não valida nada aqui
e não fala com o banco diretamente.
"""

from flask import Blueprint, jsonify, request

from controllers import cliente_controller
from utils.auth import login_required

cliente_bp = Blueprint("clientes", __name__, url_prefix="/api/clientes")


@cliente_bp.route("", methods=["GET"])
@login_required  # a lista de clientes só aparece para quem está logado
def get_clientes():
    resultado, status = cliente_controller.listar_clientes()
    return jsonify(resultado), status


@cliente_bp.route("", methods=["POST"])
def post_cliente():
    # Público: é o cadastro (quem ainda não tem conta precisa conseguir se cadastrar).
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        dados = {}
    resultado, status = cliente_controller.cadastrar_cliente(dados)
    return jsonify(resultado), status
