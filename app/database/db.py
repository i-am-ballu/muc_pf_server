import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = 3306
DB_NAME = os.getenv("DB_NAME")

print(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT)

def get_connection():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
        print('conn -------- ', conn);
        return conn

    except Exception as e:
        print("DB ERROR:", e)
        raise e

def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
