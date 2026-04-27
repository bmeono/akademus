import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()
cur.execute("SELECT id, nombre, grupo_academico_id, codigo FROM especialidades")
rows = cur.fetchall()
print(f"Found {len(rows)} especialidades")
for r in rows:
    print(f"  ID={r[0]}, nombre={r[1]}, grupo_academico_id={r[2]}, codigo={r[3]}")
conn.close()