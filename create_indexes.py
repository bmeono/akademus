import psycopg2

conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()

print("=== CREANDO INDICES FALTANTES ===")

indexes = [
    ("flashcards", "CREATE INDEX IF NOT EXISTS idx_flashcards_usuario ON flashcards(usuario_id)"),
    ("flashcards", "CREATE INDEX IF NOT EXISTS idx_flashcards_usuario_pregunta ON flashcards(usuario_id, pregunta_id)"),
    ("flashcards", "CREATE INDEX IF NOT EXISTS idx_flashcards_estado ON flashcards(estado)"),
    ("respuestas_simulacro", "CREATE INDEX IF NOT EXISTS idx_respuestas_simulacro_simulacro ON respuestas_simulacro(simulacro_id)"),
    ("respuestas_simulacro", "CREATE INDEX IF NOT EXISTS idx_respuestas_simulacro_orden ON respuestas_simulacro(simulacro_id, orden)"),
    ("simulacros", "CREATE INDEX IF NOT EXISTS idx_simulacros_usuario_estado ON simulacros(usuario_id, estado)"),
    ("resultados_detalle", "CREATE INDEX IF NOT EXISTS idx_resultados_detalle_simulacro ON resultados_detalle(simulacro_id)"),
    ("resultados_detalle", "CREATE INDEX IF NOT EXISTS idx_resultados_detalle_pregunta ON resultados_detalle(pregunta_id)"),
    ("resultados_detalle", "CREATE INDEX IF NOT EXISTS idx_resultados_detalle_usuario_simulacro ON resultados_detalle(simulacro_id)"),
]

for tabla, idx in indexes:
    try:
        cur.execute(idx)
        print(f"OK {tabla}")
    except Exception as e:
        print(f"ERROR {tabla}: {e}")

conn.commit()
print("\n=== TODOS LOS INDICES ===")
cur.execute("SELECT indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY indexname")
for row in cur.fetchall():
    print(f"- {row[0]}")

conn.close()
print("\nListo!")