"""
modules/resgates/repository.py
"""
from db.connection import get_connection


def registrar_resgate_db(usuario_id, produto_id, comanda_id, pontos_gastos, tipo) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO resgates (usuario_id, produto_id, comanda_id, pontos_gastos, tipo)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (usuario_id, produto_id, comanda_id, pontos_gastos, tipo),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def listar_resgates_usuario_db(usuario_id: int) -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT r.id, p.nome AS produto_nome, p.foto_url,
                   r.pontos_gastos, r.tipo, r.status, r.data_criacao,
                   r.comanda_id
            FROM resgates r
            INNER JOIN produtos_clube p ON p.id = r.produto_id
            WHERE r.usuario_id = %s
            ORDER BY r.data_criacao DESC
            """,
            (usuario_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
