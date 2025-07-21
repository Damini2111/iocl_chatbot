import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()  # Loads your .env file

def get_connection():
    return mysql.connector.connect(
        # host=os.getenv("MYSQL_HOST"),
        # user=os.getenv("MYSQL_USER"),
        # password=os.getenv("MYSQL_PASSWORD"),
        # database=os.getenv("MYSQL_DB")
        host='localhost',
            user='root',
            password='NewPassword123',
            database='holiday_db',
            port=3306,
            connection_timeout=10
    )
