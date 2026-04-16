"""
modules/pontos/repository.py
"""
from db.connection import get_connection


def buscar_saldo_db(usuario_id: int) -> float:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN tipo = 'ganho' THEN valor ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN tipo = 'gasto' THEN valor ELSE 0 END), 0) AS saldo
            FROM pontos
            WHERE usuario_id = %s
            """,
            (usuario_id,),
        )
        row = cursor.fetchone()
        return float(row["saldo"]) if row else 0.0
    finally:
        cursor.close()
        conn.close()


def registrar_pontos_db(usuario_id: int, tipo: str, valor: float, comanda_id: int | None, descricao: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO pontos (usuario_id, tipo, valor, comanda_id, descricao)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (usuario_id, tipo, valor, comanda_id, descricao),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def historico_pontos_db(usuario_id: int) -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT tipo, valor, descricao, data_criacao
            FROM pontos
            WHERE usuario_id = %s
            ORDER BY data_criacao DESC
            LIMIT 30
            """,
            (usuario_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def buscar_usuario_por_comanda_db(comanda_id: int) -> dict | None:
    """Encontra o usuário vinculado a uma comanda."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT usuario_id FROM usuarios_comandas
            WHERE comanda_id = %s
            """,
            (comanda_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def vincular_comanda_db(usuario_id: int, comanda_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO usuarios_comandas (usuario_id, comanda_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE usuario_id = usuario_id
            """,
            (usuario_id, comanda_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def buscar_comanda_vinculada_usuario_db(usuario_id: int) -> dict | None:
    """Retorna a comanda mais recente vinculada ao usuário."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT comanda_id, data_vinculacao
            FROM usuarios_comandas
            WHERE usuario_id = %s
            ORDER BY data_vinculacao DESC
            LIMIT 1
            """,
            (usuario_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
