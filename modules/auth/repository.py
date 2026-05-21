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


def buscar_usuarios_por_termo_db(termo: str) -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        like = f"%{termo}%"
        cursor.execute(
            """
            SELECT u.id, u.nome, u.nickname,
                   COALESCE(SUM(CASE WHEN p.tipo='ganho' THEN p.valor ELSE 0 END) -
                            SUM(CASE WHEN p.tipo='gasto'  THEN p.valor ELSE 0 END), 0) AS saldo_pontos
            FROM usuarios u
            LEFT JOIN pontos p ON p.usuario_id = u.id
            WHERE u.nome LIKE %s OR u.nickname LIKE %s
            GROUP BY u.id
            ORDER BY u.nome
            LIMIT 20
            """,
            (like, like),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def redefinir_senha_db(usuario_id: int, nova_hash: bytes):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE usuarios SET senha_hash = %s WHERE id = %s",
            (nova_hash, usuario_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def listar_todos_usuarios_db() -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT u.id, u.nome, u.nickname, u.data_criacao,
                   COALESCE(SUM(CASE WHEN p.tipo='ganho' THEN p.valor ELSE 0 END) -
                            SUM(CASE WHEN p.tipo='gasto'  THEN p.valor ELSE 0 END), 0) AS saldo_pontos
            FROM usuarios u
            LEFT JOIN pontos p ON p.usuario_id = u.id
            GROUP BY u.id
            ORDER BY u.nome
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
