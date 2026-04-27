import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()

print("=== TABLA PREGUNTAS ===")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'preguntas' ORDER BY ordinal_position")
for r in cur.fetchall(): print(f"  {r[0]}: {r[1]}")

print()
print("=== TABLA OPCIONES ===")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'opciones' ORDER BY ordinal_position")
for r in cur.fetchall(): print(f"  {r[0]}: {r[1]}")

print()
print("=== DATOS PREGUNTAS ===")
cur.execute("SELECT * FROM preguntas LIMIT 5")
for r in cur.fetchall(): print(f"  {r}")

print()
print("=== DATOS OPCIONES ===")
cur.execute("SELECT * FROM opciones LIMIT 10")
for r in cur.fetchall(): print(f"  {r}")

conn.close()