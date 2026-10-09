"""
Camada CONTROLLER.

Responsável pela regra de negócio: validar os dados recebidos
e decidir o que responder. Não conhece Flask (jsonify/request) nem
SQL diretamente — fala com o model e devolve (dados, status_http).
"""

from mysql.connector import Error as MySQLError
from mysql.connector import errorcode

from models import cliente_model
from utils import seguranca, validacoes


def listar_clientes():
    """Retorna a lista de clientes cadastrados."""
    try:
        clientes = cliente_model.listar_todos()
        return clientes, 200
    except MySQLError as erro:
        print(f"[ERRO] Falha ao listar clientes: {erro}")
        return {"success": False, "message": "Não foi possível carregar os clientes."}, 500


def _texto(valor):
    return valor.strip() if isinstance(valor, str) else ""


def cadastrar_cliente(dados):
    """Valida e cadastra um novo cliente (com senha) a partir do JSON recebido."""
    nome = _texto(dados.get("nome"))
    email = validacoes.normalizar_email(dados.get("email"))
    senha = dados.get("senha") if isinstance(dados.get("senha"), str) else ""
    telefone = _texto(dados.get("telefone"))
    cidade = _texto(dados.get("cidade"))

    if not nome or not email or not senha or not telefone or not cidade:
        return {"success": False, "message": "Preencha todos os campos."}, 400

    erro_email = validacoes.validar_email(email)
    if erro_email:
        return {"success": False, "message": erro_email}, 400

    erro_senha = validacoes.validar_senha(senha)
    if erro_senha:
        return {"success": False, "message": erro_senha}, 400

    try:
        if cliente_model.buscar_por_email(email):
            return {"success": False, "message": "Este e-mail já está cadastrado."}, 409

        novo_id = cliente_model.inserir(
            nome, email, seguranca.gerar_hash(senha), telefone, cidade
        )
        cliente = {
            "id": novo_id,
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "cidade": cidade,
        }
        return {
            "success": True,
            "message": "Cadastro realizado com sucesso!",
            "cliente": cliente,
        }, 201
    except MySQLError as erro:
        if getattr(erro, "errno", None) == errorcode.ER_DUP_ENTRY:
            return {"success": False, "message": "Este e-mail já está cadastrado."}, 409
        print(f"[ERRO] Falha ao cadastrar cliente: {erro}")
        return {"success": False, "message": "Não foi possível cadastrar o cliente."}, 500
