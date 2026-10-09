"""
Camada CONTROLLER do login.

Valida os dados (de novo, mesmo que o JavaScript já tenha validado),
confere o usuário e a senha e aplica o limite de tentativas.
Não conhece Flask: devolve (resposta, status_http, usuario_ou_None).
Quem grava a sessão é a route.
"""

import time

import config
from mysql.connector import Error as MySQLError

from models import cliente_model
from utils import seguranca, validacoes
from utils.seguranca import LimitadorTentativas

MSG_CREDENCIAIS = "E-mail ou senha inválidos."
MSG_ERRO_SERVIDOR = "Não foi possível realizar o login no momento. Tente novamente mais tarde."

# Uma chave por IP+e-mail (protege uma conta) e outra só por IP (protege contra
# alguém testando vários e-mails). Ambas bloqueiam apenas temporariamente.
limitador_conta = LimitadorTentativas(
    config.LOGIN_MAX_FALHAS, config.LOGIN_JANELA_SEGUNDOS, config.LOGIN_BLOQUEIO_SEGUNDOS
)
limitador_ip = LimitadorTentativas(
    config.LOGIN_MAX_FALHAS * 4, config.LOGIN_JANELA_SEGUNDOS, config.LOGIN_BLOQUEIO_SEGUNDOS
)

ATRASO_APOS_FALHA = 0.5  # segundos


def _erro(mensagem, status, campos=None, **extra):
    resposta = {"success": False, "message": mensagem}
    if campos:
        resposta["errors"] = campos
    resposta.update(extra)
    return resposta, status, None


def autenticar(dados, ip):
    """Valida e autentica. Retorna (resposta, status, usuario|None)."""
    email = validacoes.normalizar_email(dados.get("email"))
    senha = dados.get("senha") if isinstance(dados.get("senha"), str) else ""

    # 1) Validação dos dados enviados
    erros = {}
    erro_email = validacoes.validar_email(email)
    if erro_email:
        erros["email"] = erro_email
    erro_senha = validacoes.validar_senha(senha)
    if erro_senha:
        erros["senha"] = erro_senha
    if erros:
        return _erro(next(iter(erros.values())), 400, erros)

    # 2) Limite de tentativas (checado antes de consultar o banco)
    chave_conta = f"{ip}|{email}"
    espera = max(limitador_conta.segundos_bloqueado(chave_conta), limitador_ip.segundos_bloqueado(ip))
    if espera:
        minutos = (espera + 59) // 60
        return _erro(
            f"Muitas tentativas. Tente novamente em {minutos} minuto(s).",
            429,
            retry_after=espera,
        )

    # 3) Consulta o usuário
    try:
        cliente = cliente_model.buscar_por_email(email)
    except MySQLError as erro:
        print(f"[ERRO] Falha ao consultar usuário no login: {erro}")
        return _erro(MSG_ERRO_SERVIDOR, 500)

    # 4) Confere a senha (gasta o mesmo tempo mesmo se o usuário não existir)
    senha_hash = cliente.get("senha_hash") if cliente else None
    senha_ok = seguranca.conferir_senha(senha, senha_hash)

    if not cliente or not senha_ok:
        limitador_conta.registrar_falha(chave_conta)
        limitador_ip.registrar_falha(ip)
        time.sleep(ATRASO_APOS_FALHA)
        return _erro(MSG_CREDENCIAIS, 401)

    # 5) Sucesso
    limitador_conta.limpar(chave_conta)
    usuario = {"id": cliente["id"], "nome": cliente["nome"], "email": cliente["email"]}
    return {
        "success": True,
        "message": "Login realizado com sucesso",
        "redirect": "/dashboard",
    }, 200, usuario
