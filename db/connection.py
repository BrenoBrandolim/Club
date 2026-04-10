import mysql.connector
from mysql.connector import pooling
from config import Config

# Pool criado UMA vez quando o módulo é importado pelo Flask.
# pool_size=5 é suficiente para uso local/mono-usuário; ajuste se necessário.
_pool = pooling.MySQLConnectionPool(
    pool_name="newbox_pool",
    pool_size=5,
    pool_reset_session=True,          # garante sessão limpa entre reusos
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME,
    charset="utf8mb4",
    autocommit=False,
)


def get_connection():
    """
    Retorna uma conexão do pool.
    Use sempre em bloco with/try-finally para garantir devolução ao pool:

        conn = get_connection()
        try:
            ...
        finally:
            conn.close()   # devolve ao pool, NÃO fecha o socket
    """
    return _pool.get_connection()
