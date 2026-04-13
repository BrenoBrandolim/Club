from db.connection import get_connection


# Buscar produto (pode usar conexão própria - leitura simples)
def buscar_produto_por_id_db(produto_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, nome, pontos_necessarios, ativo
                FROM produtos_clube
                WHERE id = %s
            """, (produto_id,))

            return cursor.fetchone()
        finally:
            cursor.close()
    finally:
        conn.close()


# Criar resgate (usa conexão do service)
def criar_resgate_db(conn, usuario_id, produto_id, comanda_id, pontos):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO resgates
            (usuario_id, produto_id, comanda_id, pontos_gastos, tipo)
            VALUES (%s, %s, %s, %s, 'local')
        """, (usuario_id, produto_id, comanda_id, pontos))

        return cursor.lastrowid
    finally:
        cursor.close()


# Debitar pontos (usa conexão do service)
def debitar_pontos_db(conn, usuario_id, valor, comanda_id):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO pontos (usuario_id, tipo, valor, comanda_id, descricao)
            VALUES (%s, 'gasto', %s, %s, %s)
        """, (
            usuario_id,
            valor,
            comanda_id,
            f"Resgate na comanda {comanda_id}"
        ))
    finally:
        cursor.close()