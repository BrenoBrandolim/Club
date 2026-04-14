from db.connection import get_connection

def listar_produtos_db():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, pontos_necessarios, preco_dinheiro
            FROM produtos_clube
            WHERE ativo = TRUE
        """)

        return cursor.fetchall()
    finally:
        conn.close()