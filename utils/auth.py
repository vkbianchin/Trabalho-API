"""
Controle de acesso: verifica se existe sessão de login e protege rotas.
"""

from functools import wraps

from flask import jsonify, redirect, request, session, url_for


def usuario_logado():
    return bool(session.get("usuario_id"))


def login_required(funcao):
    """
    Protege uma rota. Sem login:
      - páginas (HTML) redirecionam para /login;
      - rotas da API (/api/...) respondem 401 em JSON.
    """

    @wraps(funcao)
    def protegida(*args, **kwargs):
        if usuario_logado():
            return funcao(*args, **kwargs)

        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "message": "Sessão expirada. Faça login novamente.",
                "redirect": "/login",
            }), 401

        return redirect(url_for("auth.pagina_login"))

    return protegida
