from datetime import timedelta

from flask import Flask, jsonify, request

import config
from routes.auth_routes import auth_bp
from routes.cliente_routes import cliente_bp
from routes.main_routes import main_bp

app = Flask(__name__)

app.config.update(
    SECRET_KEY=config.SECRET_KEY,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=config.SESSION_COOKIE_SECURE,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=config.SESSION_HORAS),
    MAX_CONTENT_LENGTH=64 * 1024,  # requisições de formulário pequenas
)

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(cliente_bp)

if not config.SECRET_KEY_DEFINIDA:
    print("[AVISO] SECRET_KEY não está no .env. Usando chave temporária: "
          "os logins serão perdidos quando o servidor reiniciar.")


@app.after_request
def cabecalhos_de_seguranca(resposta):
    # Páginas e APIs nunca ficam em cache: depois do logout, o botão "Voltar"
    # do navegador não consegue mostrar uma página protegida guardada.
    if request.endpoint != "static":
        resposta.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resposta.headers["Pragma"] = "no-cache"
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["X-Frame-Options"] = "DENY"
    return resposta


@app.errorhandler(413)
def corpo_muito_grande(_erro):
    return jsonify({"success": False, "message": "Requisição muito grande."}), 413


@app.errorhandler(500)
def erro_interno(_erro):
    # Nunca mostra detalhes técnicos ao usuário.
    return jsonify({"success": False, "message": "Erro interno do servidor. Tente novamente mais tarde."}), 500


if __name__ == "__main__":
    app.run(debug=True)
