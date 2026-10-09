"""
Camada MODEL.

Responsável apenas por falar com o MySQL:
abrir conexão, executar SQL, fechar cursor/conexão.
Não faz validação de regra de negócio (isso fica no controller).
"""

import mysql.connector

from config import DB_CONFIG


def get_connection():
    """Cria e retorna uma nova conexão com o MySQL."""
    return mysql.connector.connect(**DB_CONFIG)


def listar_todos():
    """Busca todos os clientes no banco, ordenados por id crescente."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nome, email, telefone, cidade FROM clientes ORDER BY id ASC"
        )
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def buscar_por_email(email):
    """
    Busca um cliente pelo e-mail (SQL parametrizado).
    Retorna dict (id, nome, email, senha_hash) ou None. Usado no login e
    para evitar e-mail duplicado no cadastro.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nome, email, senha_hash FROM clientes WHERE email = %s LIMIT 1",
            (email,),
        )
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def inserir(nome, email, senha_hash, telefone, cidade):
    """Insere um novo cliente (SQL parametrizado) e retorna o id gerado."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO clientes (nome, email, senha_hash, telefone, cidade)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nome, email, senha_hash, telefone, cidade),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
