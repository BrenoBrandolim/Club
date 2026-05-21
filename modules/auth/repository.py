"""
modules/auth/repository.py
"""
from db.connection import get_connection


def criar_usuario_db(nome: str, nickname: str, senha_hash: bytes):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, nickname, senha_hash) VALUES (%s, %s, %s)",
            (nome, nickname, senha_hash),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def buscar_por_nickname_db(nickname: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, nome, nickname, senha_hash FROM usuarios WHERE nickname = %s",
            (nickname,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def buscar_usuario_por_id_db(usuario_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, nome, nickname FROM usuarios WHERE id = %s",
            (usuario_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
