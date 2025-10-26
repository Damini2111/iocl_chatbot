# test_db.py
from db import get_connection

conn = get_connection()
  
if conn:
    print("🎉 Test successful!")
    conn.close()
else:
    print("💥 Could not connect.")




