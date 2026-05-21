print("🔥 EXECUTANDO TESTE_DB")

from db.connection import get_connection

print("Tentando conectar...")
import db.connection
print("USANDO:", db.connection.__file__)

conn = get_connection()

print("Conectou!")

cursor = conn.cursor()
cursor.execute("SELECT 1")

print("Resultado:", cursor.fetchone())

cursor.close()
conn.close()
