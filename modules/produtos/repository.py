from db.connection import get_connection

def listar_produtos_db():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, pontos_necessarios, preco_dinheiro, foto_url, item_id
            FROM produtos_clube
            WHERE ativo = TRUE
        """)

        return cursor.fetchall()
    finally:
        conn.close()


def upsert_produto_db(data):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO produtos_clube (
                item_id,
                nome,
                pontos_necessarios,
                preco_dinheiro,
                foto_url,
                ativo
            )
            VALUES (%s, %s, %s, %s, %s, TRUE)
            ON DUPLICATE KEY UPDATE
                nome = VALUES(nome),
                pontos_necessarios = VALUES(pontos_necessarios),
                preco_dinheiro = VALUES(preco_dinheiro),
                foto_url = VALUES(foto_url),
                ativo = TRUE
        """, (
            data["item_id"],
            data["nome"],
            data["pontos"],
            data["preco_dinheiro"],
            data["foto_url"]
        ))

        conn.commit()
    finally:
        conn.close()