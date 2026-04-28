import sqlite3

db_path = 'C:/Users/Brian/Desktop/akademus/backend/akademus.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)

# Count preguntas
cur.execute('SELECT COUNT(*) FROM preguntas')
print(f'Local preguntas: {cur.fetchone()[0]}')

# Count opciones
cur.execute('SELECT COUNT(*) FROM opciones')
print(f'Local opciones: {cur.fetchone()[0]}')

# Check with options
cur.execute('SELECT COUNT(DISTINCT pregunta_id) FROM opciones WHERE pregunta_id IS NOT NULL')
print(f'Local con opciones: {cur.fetchone()[0]}')

# Get sample opciones
cur.execute('SELECT p.id, p.enunciado, o.id, o.texto, o.es_correcta FROM preguntas p JOIN opciones o ON p.id = o.pregunta_id LIMIT 3')
for r in cur.fetchall():
    print(f'Pregunta {r[0]}: {r[1][:30]}... | Opcion {r[2]}: {r[3]} (correcta: {r[4]})')

conn.close()