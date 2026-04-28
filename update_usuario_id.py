import psycopg2

conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()

# Update usuario_id in resultados_detalle from simulacros table
cur.execute("""
    UPDATE resultados_detalle rd
    SET usuario_id = s.usuario_id
    FROM simulacros s
    WHERE rd.simulacro_id = s.id
    AND rd.usuario_id IS NULL
""")
print(f"Updated {cur.rowcount} rows")

conn.commit()
conn.close()
print("Done!")