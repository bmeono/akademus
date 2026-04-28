import psycopg2

conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()

print("=== ESQUEMA DE TABLAS ===")
tablas = ['resultados_detalle', 'flashcards', 'respuestas_simulacro', 'simulacros']
for tabla in tablas:
    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{tabla}' ORDER BY ordinal_position")
    cols = [r[0] for r in cur.fetchall()]
    print(f"\n{tabla}:")
    for c in cols:
        print(f"  - {c}")

conn.close()