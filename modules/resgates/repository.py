from db.connection import get_connection

def buscar_produto_por_id_db(produto_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, pontos_necessarios, ativo
            FROM produtos_clube
            WHERE id = %s """, (produto_id,)
        )

        return cursor.fetchone()
    finally:
        conn.close()

def criar_resgate_db(usuario_id, produto_id, comanda_id, pontos):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO resgates
            (usuario_id, produto_id, comanda_id, pontos_gastos, tipo)
            VALUES (%s, %s, %s, %s, 'local') """,
            (usuario_id, produto_id, comanda_id, pontos)   
        )

        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def debitar_pontos_db(usuario_id, valor, comanda_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pontos (usuario_id, tipo, valor, comanda_id, descricao)
            VALUES (%s, 'gasto', %s, %s, %s)
        """, (
            usuario_id,
            valor,
            comanda_id,
            f"Resgate na comanda {comanda_id}"
        ))

        conn.commit()
    finally:
        conn.close()