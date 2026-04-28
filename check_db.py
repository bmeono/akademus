import psycopg2
conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()
cur.execute("SELECT tablename, indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname")
print("=== ÍNDICES EXISTENTES ===")
for row in cur.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\n=== CONTEO DE TABLAS ===")
tablas = ['usuarios', 'preguntas', 'opciones', 'simulacros', 'resultados_detalle', 'flashcards', 'respuestas_simulacro']
for tabla in tablas:
    cur.execute(f"SELECT COUNT(*) FROM {tabla}")
    print(f"{tabla}: {cur.fetchone()[0]}")

conn.close()