# db.py
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()
print("🔍 Host from .env:", os.getenv("MYSQL_HOST"))


def get_connection():
    try:
        return mysql.connector.connect(
            host='localhost', #os.getenv("MYSQL_HOST"),  # should be 127.0.0.1
            user='root', #os.getenv("MYSQL_USER"),
            password='NewPassword123', #os.getenv("MYSQL_PASSWORD"),
            database='holidy_db', # os.getenv("MYSQL_DB"),
            port=3306,
            connection_timeout=10
        )
    except mysql.connector.Error as err:
        print("❌ Connection failed:", err)
        return None
