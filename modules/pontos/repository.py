from db.connection import get_connection

def calcular_saldo_usuario_db(usuario_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN tipo = 'ganho' THEN valor ELSE 0 END), 0) as ganhos,
                COALESCE(SUM(CASE WHEN tipo = 'gasto' THEN valor ELSE 0 END), 0) as gastos
            FROM pontos
            WHERE usuario_id = %s
        """, (usuario_id,))

        resultado = cursor.fetchone()

        saldo = resultado['ganhos'] - resultado['gastos']

        return saldo
    
    finally:
        conn.close()