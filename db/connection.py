import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

class MyConnection:
    def __init__(self):
        self.conn = pymysql.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "admin123"),
            database=os.getenv("DB_NAME"),
            port=3306
        )

    def cursor(self, dictionary=False):
        if dictionary:
            return self.conn.cursor(pymysql.cursors.DictCursor)
        return self.conn.cursor()

    def commit(self):
        return self.conn.commit()

    def close(self):
        return self.conn.close()


def get_connection():
    print("🔌 Conectando com pymysql...")
    return MyConnection()