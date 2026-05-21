"""
modules/produtos/repository.py
"""
from db.connection import get_connection


def listar_produtos_db() -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, nome, foto_url, pontos_necessarios, preco_dinheiro, ativo, item_id
            FROM produtos_clube
            WHERE ativo = TRUE
            ORDER BY pontos_necessarios ASC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def buscar_produto_por_id_db(produto_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM produtos_clube WHERE id = %s",
            (produto_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def upsert_produto_db(item_id: int, nome: str, pontos: float, preco_dinheiro: float, foto_url: str):
    """
    Insere ou atualiza produto do clube pelo item_id do Caixa.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO produtos_clube (item_id, nome, pontos_necessarios, preco_dinheiro, foto_url, ativo)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            ON DUPLICATE KEY UPDATE
                nome              = VALUES(nome),
                pontos_necessarios= VALUES(pontos_necessarios),
                preco_dinheiro    = VALUES(preco_dinheiro),
                foto_url          = VALUES(foto_url),
                ativo             = TRUE
            """,
            (item_id, nome, pontos, preco_dinheiro, foto_url),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def editar_produto_db(produto_id: int, nome: str, foto_url: str, pontos: float, ativo: bool):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE produtos_clube
            SET nome = %s, foto_url = %s, pontos_necessarios = %s, ativo = %s
            WHERE id = %s
            """,
            (nome, foto_url, pontos, ativo, produto_id),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()
