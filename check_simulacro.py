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

print("=== Simulacro 18 (ultimo) ===")
# Total preguntas en el simulacro
cur.execute("SELECT total_preguntas FROM simulacros WHERE id = '18'", (user_id,))
total = cur.fetchone()
print(f"Total preguntas en simulacro: {total[0]}")

# Cómo se respondió cada pregunta
cur.execute("""
    SELECT 
        CASE 
            WHEN rs.respuesta IS NULL THEN 'NO RESPONDIDA'
            WHEN rd.es_correcta = TRUE THEN 'CORRECTA'
            WHEN rd.es_correcta = FALSE THEN 'INCORRECTA'
        END as estado,
        COUNT(*)
    FROM respuestas_simulacro rs
    LEFT JOIN resultados_detalle rd ON rd.simulacro_id = rs.simulacro_id AND rd.pregunta_id = rs.pregunta_id
    WHERE rs.simulacro_id = '18'
    GROUP BY CASE 
            WHEN rs.respuesta IS NULL THEN 'NO RESPONDIDA'
            WHEN rd.es_correcta = TRUE THEN 'CORRECTA'
            WHEN rd.es_correcta = FALSE THEN 'INCORRECTA'
        END
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

# Qué cuenta actualmente como "error"
cur.execute("""
    SELECT COUNT(*)
    FROM resultados_detalle rd
    WHERE rd.simulacro_id = '18' AND rd.es_correcta = FALSE
""")
errores = cur.fetchone()
print(f"\nErrores actual (es_correcta = FALSE): {errores[0]}")

#Qué debería ser (solo mal respondidas, no las NO respondidas)
cur.execute("""
    SELECT COUNT(*)
    FROM respuestas_simulacro rs
    LEFT JOIN resultados_detalle rd ON rd.simulacro_id = rs.simulacro_id AND rd.pregunta_id = rs.pregunta_id
    WHERE rs.simulacro_id = '18' 
    AND rs.respuesta IS NOT NULL 
    AND rd.es_correcta = FALSE
""")
mal_respondidas = cur.fetchone()
print(f"Mal respondidas (solo las q respondio mal): {mal_respondidas[0]}")

conn.close()