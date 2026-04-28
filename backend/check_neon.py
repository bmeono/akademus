import psycopg2
c = psycopg2.connect("postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require")
r = c.cursor()

tables = ['usuarios', 'areas', 'asignaturas', 'especialidades', 'preguntas', 'opciones', 'simulacros', 'respuestas_simulacro', 'resultados_detalle', 'roles']

for t in tables:
    r.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"{t}: {r.fetchone()[0]}")

c.close()