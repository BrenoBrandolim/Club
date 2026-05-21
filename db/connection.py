import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Railway injeta MYSQLHOST/MYSQLUSER/MYSQLPASSWORD/MYSQLDATABASE/MYSQLPORT
# Localmente usamos DB_HOST/DB_USER/DB_PASSWORD/DB_NAME
def _build_conn():
    return pymysql.connect(
        host     = os.getenv("MYSQLHOST")     or os.getenv("DB_HOST",     "127.0.0.1"),
        user     = os.getenv("MYSQLUSER")     or os.getenv("DB_USER",     "root"),
        password = os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASSWORD", ""),
        database = os.getenv("MYSQLDATABASE") or os.getenv("DB_NAME",     "BancoClube"),
        port     = int(os.getenv("MYSQLPORT") or os.getenv("DB_PORT",     3306)),
    )


class MyConnection:
    def __init__(self):
        self.conn = _build_conn()

    def cursor(self, dictionary=False):
        if dictionary:
            return self.conn.cursor(pymysql.cursors.DictCursor)
        return self.conn.cursor()

    def commit(self):
        return self.conn.commit()

    def close(self):
        return self.conn.close()


def get_connection():
    return MyConnection()
