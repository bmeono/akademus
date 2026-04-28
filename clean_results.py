import psycopg2

conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()

# Delete records where user didn't answer (es_correcta should be NULL or we shouldn't have saved at all)
# Only keep records where user actually answered (opcion_seleccionada_id IS NOT NULL)

print("=== Eliminando registros donde NO se respondió (opcion_seleccionada_id IS NULL) ===")
cur.execute("DELETE FROM resultados_detalle WHERE opcion_seleccionada_id IS NULL")
deleted = cur.rowcount
print(f"Eliminados: {deleted}")

# Check for user brmenoca
user_id = '5879fc11-4c3c-4799-bbc1-9933ae268a1d'
print(f"\n=== Resultados para usuario (solo los q respondio mal) ===")
cur.execute("""
    SELECT s.id, s.estado, s.puntaje_total,
           (SELECT COUNT(*) FROM resultados_detalle rd WHERE rd.simulacro_id = s.id AND rd.es_correcta = FALSE) as errores
    FROM simulacros s
    WHERE s.usuario_id = %s AND s.estado = 'finalizado'
    ORDER BY s.created_at DESC
""", (user_id,))
for r in cur.fetchall():
    print(f"  Simulacro {r[0]}: estado={r[1]}, puntaje={r[2]}, errores={r[3]}")

# Check by subject
print(f"\n=== Errores por asignatura (solo mal respondidas) ===")
cur.execute("""
    SELECT a.nombre, COUNT(rd.pregunta_id)
    FROM resultados_detalle rd
    JOIN simulacros s ON s.id = rd.simulacro_id
    JOIN preguntas p ON p.id = rd.pregunta_id
    JOIN asignaturas a ON a.id = p.asignatura_id
    WHERE s.usuario_id = %s AND rd.es_correcta = FALSE
    GROUP BY a.nombre
    ORDER BY COUNT(rd.pregunta_id) DESC
""", (user_id,))
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} errores")

conn.commit()
conn.close()
print("\nListo!")