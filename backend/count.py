import psycopg2

src = psycopg2.connect(host="db.czhvprbxvhqpprgaiqjd.supabase.co", port=5432, user="postgres", password="1323Bri@ncisc0", database="postgres")
dst = psycopg2.connect("postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require")

c_src = src.cursor()
c_dst = dst.cursor()

# Migrate key tables
tables = ["usuarios", "roles", "areas", "asignaturas", "especialidades", "preguntas", "opciones", "simulacros", "respuestas_simulacro", "resultados_detalle", "flashcards"]

for t in tables:
    print(f"{t}...", end=" ")
    c_src.execute(f"SELECT COUNT(*) FROM {t}")
    count = c_src.fetchone()[0]
    print(f"{count}")

src.close()
dst.close()