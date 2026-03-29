import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12821632",
        password="xRfIvBrG5d",
        database="sql12821632",
        port=3306
    )
