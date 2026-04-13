from db.connection import get_connection

def verificar_comanda_vinculada_db(comanda_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id from usuarios_comandas
            WHERE comanda_id = %s""", (comanda_id,)
        )

        return cursor.fetchone()
    
    finally:
        conn.close()

def criar_vinculo_comanda_db(comanda_id, usuario_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO usuarios_comandas (comanda_id, usuario_id)
            VALUES (%s, %s)""", (comanda_id, usuario_id)   
        )

        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def buscar_vinculo_completo_db(comanda_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT usuario_id, processada 
            FROM usuarios_comandas
            WHERE comanda_id = %s""", (comanda_id,)
        )

        return cursor.fetchone()
    
    finally:
        conn.close()


def inserir_pontos_db(usuario_id, valor, comanda_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pontos (usuario_id, tipo, valor, comanda_id, descricao)
            VALUES (%s, 'ganho', %s, %s, %s)
        """, (
            usuario_id,
            valor,
            comanda_id,
            f"Pontos da comanda {comanda_id}"
        ))

        conn.commit()
    finally:
        conn.close()

def marcar_comanda_processada_db(comanda_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE usuarios_comandas
            SET processada = TRUE
            WHERE comanda_id = %s
        """, (comanda_id,))

        conn.commit()
    finally:
        conn.close()