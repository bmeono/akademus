import psycopg2

conn = psycopg2.connect(
    host="db.czhvprbxvhqpprgaiqjd.supabase.co",
    port=5432,
    user="postgres",
    password="1323Bri@ncisc0",
    database="postgres"
)

cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = [r[0] for r in cur.fetchall()]
print(f"Tablas en Supabase ({len(tables)}): {tables}")

for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  {t}: {cur.fetchone()[0]} filas")

conn.close()