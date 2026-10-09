"""
Validações compartilhadas entre cadastro e login (e-mail e senha).

A mesma regra existe no front-end (static/Js/validacoes.js). O back-end
valida de novo porque nunca se deve confiar apenas no JavaScript.
"""

import re

TAMANHO_MIN_SENHA = 8
TAMANHO_MAX_SENHA = 128
TAMANHO_MAX_EMAIL = 150

# texto@dominio.com (aceita também .com.br, .com.pt etc.)
EMAIL_REGEX = re.compile(
    r"[A-Za-z0-9_%+\-]+(?:\.[A-Za-z0-9_%+\-]+)*"
    r"@"
    r"[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*"
    r"\.com(?:\.[A-Za-z]{2})?"
)

CARACTERES_ESPECIAIS = set("!@#$%^&*()_+-=[]{};':\"\\|,.<>/?`~")


def normalizar_email(email):
    """Remove espaços externos e coloca em minúsculas. Não-texto vira ''."""
    if not isinstance(email, str):
        return ""
    return email.strip().lower()


def validar_email(email):
    """Retorna None se o e-mail é válido, ou a mensagem de erro."""
    if not email:
        return "O e-mail é obrigatório."
    if any(c.isspace() for c in email):
        return "O e-mail não pode conter espaços."
    if "@" not in email or ".com" not in email:
        return "O e-mail deve possuir @ e .com."
    if len(email) > TAMANHO_MAX_EMAIL or not EMAIL_REGEX.fullmatch(email):
        return "Digite um e-mail válido."
    return None


def requisitos_senha(senha):
    """Diz quais requisitos a senha cumpre."""
    return {
        "tamanho": len(senha) >= TAMANHO_MIN_SENHA,
        "maiuscula": any("A" <= c <= "Z" for c in senha),
        "minuscula": any("a" <= c <= "z" for c in senha),
        "numero": any("0" <= c <= "9" for c in senha),
        "especial": any(c in CARACTERES_ESPECIAIS for c in senha),
    }


def validar_senha(senha):
    """Retorna None se a senha é válida, ou a mensagem de erro."""
    if not isinstance(senha, str) or not senha:
        return "A senha é obrigatória."
    if len(senha) > TAMANHO_MAX_SENHA or not all(requisitos_senha(senha).values()):
        return "A senha não atende aos requisitos de segurança."
    return None
