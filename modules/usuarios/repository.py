from db.connection import get_connection

def criar_usuario(nome, nickname, senha_hash):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO usuarios (nome, nickname, senha_hash)
            VALUES (%s, %s, %s)""", (nome, nickname, senha_hash)   
        )

        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def buscar_por_nickname(nickname):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, nickname, senha_hash
            FROM usuarios
            WHERE nickname = %s""", (nickname,)
        )
 
        return cursor.fetchone() is not None
    finally:
        conn.close()


def buscar_usuario_por_id(usuario_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, nickname, senha_hash
            FROM usuarios
            WHERE id = %s""", (usuario_id,)
        )

        return cursor.fetchone() is not None
    finally:
        conn.close()
        
                    