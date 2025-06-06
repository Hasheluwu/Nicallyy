import sqlite3
import os

def get_con_connection():
    db_path = os.path.abspath("users.db")
    print(f"Ruta absoluta de la base de datos: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con

con = get_con_connection()

tablas = [
    "user_achievements",
    "user_trivias",
    "user_responses",
    "responses",
    "questions",
    "trivias",
    "achievements",
    "categories",
    "users"
]

print("\nTablas antes de borrar:")
cursor = con.execute("SELECT name FROM sqlite_master WHERE type='table';")
for row in cursor.fetchall():
    print("-", row["name"])

print("\nEliminando tablas...")
for tabla in tablas:
    try:
        con.execute(f"DROP TABLE IF EXISTS {tabla};")
        print(f"Eliminada: {tabla}")
    except Exception as e:
        print(f"Error al eliminar {tabla}: {e}")
con.commit()

print("\nTablas después de borrar:")
cursor = con.execute("SELECT name FROM sqlite_master WHERE type='table';")
for row in cursor.fetchall():
    print("-", row["name"])

con.close()
