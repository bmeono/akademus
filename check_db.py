import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
print('Tables:', [r[0] for r in cur.fetchall()])

print()
print('=== BLOQUES_TEMATICOS ===')
cur.execute('SELECT * FROM bloques_tematicos ORDER BY orden')
for r in cur.fetchall(): print(r)

print()
print('=== AREAS ===')
cur.execute('SELECT * FROM areas ORDER BY orden')
for r in cur.fetchall(): print(r)

print()
print('=== ASIGNATURAS ===')
cur.execute('SELECT * FROM asignaturas ORDER BY orden')
for r in cur.fetchall(): print(r)

print()
print('=== GRUPOS_ACADEMICOS ===')
cur.execute('SELECT * FROM grupos_academicos ORDER BY orden')
for r in cur.fetchall(): print(r)

print()
print('=== ESPECIALIDADES ===')
cur.execute('SELECT * FROM especialidades ORDER BY id')
for r in cur.fetchall(): print(r)

print()
print('=== CONFIGURACIONES_PUNTAJE ===')
cur.execute('SELECT * FROM configuraciones_puntaje ORDER BY id')
for r in cur.fetchall(): print(r)

conn.close()