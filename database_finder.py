import sqlite3
import os

def get_con_connection():
    db_path = os.path.abspath("users.db")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    print(f"Ruta absoluta de la base de datos conectada: {db_path}")
    return con

con = get_con_connection()

print("Tablas en la base de datos:")
cursor = con.execute("SELECT name FROM sqlite_master WHERE type='table';")
for row in cursor.fetchall():
    print("-", row["name"])

con.close()

