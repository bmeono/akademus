from app.core.security import get_db_connection

conn = get_db_connection()
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
print("Tablas locales:", [r[0] for r in cur.fetchall()])
conn.close()