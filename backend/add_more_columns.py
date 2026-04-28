import psycopg2

conn = psycopg2.connect("postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require")
cur = conn.cursor()

# Add missing columns
columns = [
    ("usuarios", "ultima_actividad", "TIMESTAMP"),
    ("simulacros", "puntaje_total", "DECIMAL"),
    ("simulacros", "respuestas_correctas", "INTEGER"),
    ("simulacros", "respuestas_incorrectas", "INTEGER"),
    ("simulacros", "grupo_academico_id", "INTEGER"),
    ("simulacros", "especialidad_id", "INTEGER"),
    ("simulacros", "estado", "VARCHAR(20)"),
    ("respuestas_simulacro", "respuesta", "TEXT"),
    ("respuestas_simulacro", "puntaje", "DECIMAL"),
    ("respuestas_simulacro", "tiempo_segundos", "INTEGER"),
    ("resultados_detalle", "opcion_seleccionada_id", "INTEGER"),
]

for table, col, type_ in columns:
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {type_}")
        conn.commit()
        print(f"Added {col} to {table}")
    except:
        conn.rollback()

conn.close()
print("Done!")