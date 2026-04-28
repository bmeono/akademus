import sqlite3

conn = sqlite3.connect("akademus.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print(f"Tablas ({len(tables)}): {[t[0] for t in tables]}")
conn.close()