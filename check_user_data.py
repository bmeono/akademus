import psycopg2

conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()

user_id = '5879fc11-4c3c-4799-bbc1-9933ae268a1d'

print("=== Simulacros del usuario ===")
cur.execute("SELECT id, estado, puntaje_total, created_at FROM simulacros WHERE usuario_id = %s ORDER BY created_at DESC", (user_id,))
for s in cur.fetchall():
    print(f"  Simulacro {s[0]}: estado={s[1]}, puntaje={s[2]}, fecha={s[3]}")

print("\n=== Resultados detalle (errores por simulacro) ===")
cur.execute("""
    SELECT s.id, COUNT(rd.pregunta_id), 
           SUM(CASE WHEN rd.es_correcta = FALSE THEN 1 ELSE 0 END) as errores
    FROM resultados_detalle rd
    JOIN simulacros s ON s.id = rd.simulacro_id
    WHERE s.usuario_id = %s
    GROUP BY s.id
    ORDER BY s.id
""", (user_id,))
for r in cur.fetchall():
    print(f"  Simulacro {r[0]}: {r[1]} preg, {r[2]} errores")

print("\n=== Errores por asignatura (ASIGNATURAS) ===")
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

conn.close()