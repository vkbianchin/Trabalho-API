import os
import secrets

from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "aluno05"),
    "password": os.getenv("DB_PASSWORD", "C@nes2026"),
    "database": os.getenv("DB_NAME", "cadastro_clientes"),
}

# ---- Login / sessão -------------------------------------------------
# Defina SECRET_KEY no .env. Sem ela, uma chave temporária é criada a cada
# inicialização e todos os usuários perdem o login quando o servidor reinicia.
SECRET_KEY_DEFINIDA = bool(os.getenv("SECRET_KEY"))
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# Use "true" apenas quando o site rodar em HTTPS.
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
SESSION_HORAS = int(os.getenv("SESSION_HORAS", "8"))

# Limite de tentativas: após N falhas na janela, bloqueia temporariamente.
LOGIN_MAX_FALHAS = int(os.getenv("LOGIN_MAX_FALHAS", "5"))
LOGIN_JANELA_SEGUNDOS = int(os.getenv("LOGIN_JANELA_SEGUNDOS", "900"))
LOGIN_BLOQUEIO_SEGUNDOS = int(os.getenv("LOGIN_BLOQUEIO_SEGUNDOS", "300"))
