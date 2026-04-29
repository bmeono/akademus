import psycopg2
from psycopg2 import sql

# Conexión a Neon
conn = psycopg2.connect(
    host="ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech",
    port=5432,
    user="neondb_owner",
    password="npg_uIUNP0ZR4bzO",
    dbname="neondb",
    sslmode="require"
)

cur = conn.cursor()

# Índices a crear
indexes = [
    ("idx_opciones_pregunta", "CREATE INDEX IF NOT EXISTS idx_opciones_pregunta ON opciones(pregunta_id)"),
    ("idx_preguntas_tema", "CREATE INDEX IF NOT EXISTS idx_preguntas_tema ON preguntas(tema_id)"),
    ("idx_preguntas_asignatura", "CREATE INDEX IF NOT EXISTS idx_preguntas_asignatura ON preguntas(asignatura_id)"),
    ("idx_preguntas_usuario", "CREATE INDEX IF NOT EXISTS idx_preguntas_usuario ON preguntas(usuario_id)"),
    ("idx_preguntas_estado", "CREATE INDEX IF NOT EXISTS idx_preguntas_estado ON preguntas(estado)"),
    ("idx_respuestas_simulacro_pregunta", "CREATE INDEX IF NOT EXISTS idx_respuestas_simulacro_pregunta ON respuestas_simulacro(pregunta_id)"),
    ("idx_respuestas_simulacro_simulacro", "CREATE INDEX IF NOT EXISTS idx_respuestas_simulacro_simulacro ON respuestas_simulacro(simulacro_id)"),
    ("idx_simulacros_estado", "CREATE INDEX IF NOT EXISTS idx_simulacros_estado ON simulacros(estado)"),
    ("idx_simulacros_usuario", "CREATE INDEX IF NOT EXISTS idx_simulacros_usuario ON simulacros(usuario_id)"),
    ("idx_resultados_detalle_simulacro", "CREATE INDEX IF NOT EXISTS idx_resultados_detalle_simulacro ON resultados_detalle(simulacro_id)"),
    ("idx_resultados_detalle_correcta", "CREATE INDEX IF NOT EXISTS idx_resultados_detalle_correcta ON resultados_detalle(es_correcta)"),
    ("idx_flashcards_usuario", "CREATE INDEX IF NOT EXISTS idx_flashcards_usuario ON flashcards(usuario_id)"),
    ("idx_flashcards_pregunta", "CREATE INDEX IF NOT EXISTS idx_flashcards_pregunta ON flashcards(pregunta_id)"),
    ("idx_usuario_permisos_usuario", "CREATE INDEX IF NOT EXISTS idx_usuario_permisos_usuario ON usuario_permisos(usuario_id)"),
]

for name, query in indexes:
    try:
        cur.execute(query)
        print(f"OK: {name}")
    except Exception as e:
        print(f"ERROR: {name}: {e}")

conn.commit()
cur.close()
conn.close()

print("\n¡Índices creados exitosamente!")