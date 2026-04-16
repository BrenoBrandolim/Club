"""
db/connection.py — Club
Conexão com o banco BancoClube.
"""

import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

_pool = pooling.MySQLConnectionPool(
    pool_name="club_pool",
    pool_size=5,
    host=os.getenv("DB_HOST", "127.0.0.1"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "1234"),
    database=os.getenv("DB_NAME_CLUB", "BancoClube"),
    charset="utf8mb4",
    autocommit=False,
)


def get_connection():
    return _pool.get_connection()
