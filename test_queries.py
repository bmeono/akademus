import psycopg2
import time
conn = psycopg2.connect('postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require')
cur = conn.cursor()

# Test query times
tests = [
    ('Preguntas', "SELECT COUNT(*) FROM preguntas WHERE estado = 'aprobado' OR estado IS NULL"),
    ('Opciones', 'SELECT COUNT(*) FROM opciones'),
    ('Simulacros', 'SELECT COUNT(*) FROM simulacros'),
    ('Respuestas', 'SELECT COUNT(*) FROM respuestas_simulacro'),
]

for name, sql in tests:
    start = time.time()
    cur.execute(sql)
    cur.fetchall()
    print(f'{name}: {time.time()-start:.3f}s')