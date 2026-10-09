"""
Rotas de autenticação: página de login, POST /login e POST /logout.

Só cuida do HTTP e da sessão; a regra de negócio fica no auth_controller.
"""

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from controllers import auth_controller
from utils.auth import usuario_logado

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET"])
def pagina_login():
    # Quem já está logado não precisa ver a tela de login de novo.
    if usuario_logado():
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")


@auth_bp.route("/login", methods=["POST"])
def post_login():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        dados = {}

    ip = request.remote_addr or "desconhecido"
    resultado, status, usuario = auth_controller.autenticar(dados, ip)

    if usuario:
        # Limpa qualquer sessão anterior antes de criar a nova (evita fixação de sessão).
        session.clear()
        session["usuario_id"] = usuario["id"]
        session["usuario_nome"] = usuario["nome"]
        session.permanent = True

    resposta = jsonify(resultado)
    if status == 429 and "retry_after" in resultado:
        resposta.headers["Retry-After"] = str(resultado["retry_after"])
    return resposta, status


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logout realizado com sucesso",
        "redirect": "/login",
    })
