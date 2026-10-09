"""
Rotas das páginas (HTML).

  /           -> manda para /login (ou /dashboard se já estiver logado)
  /cadastro   -> tela de cadastro (pública)
  /dashboard  -> página principal (exige login)
"""

from flask import Blueprint, redirect, render_template, session, url_for

from utils.auth import login_required, usuario_logado

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if usuario_logado():
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.pagina_login"))


@main_bp.route("/cadastro")
def cadastro():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", nome=session.get("usuario_nome", ""))
