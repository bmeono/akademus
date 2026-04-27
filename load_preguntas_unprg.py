import psycopg2
import json

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()

# Mapping area -> asignatura_id
mapping = {
    'Razonamiento Verbal': 73,
    'Razonamiento Matemático': 74,
    'Aritmética': 75,
    'Geometría': 76,
    'Trigonometría': 78,
    'Lenguaje': 79,
    'Literatura': 80,
    'Psicología': 81,
    'Cívica': 82,
    'Historia': 83,
    'Geografía': 84,
    'Economía': 85,
    'Filosofía': 86,
    'Física': 87,
    'Química': 88,
    'Biología': 89,
    'Anatomía': 90,
}

# Cargar JSON
with open(r'C:\Users\Brian\Desktop\akademus\UNPRG_SOLUCIONARIO_2024_II.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

preguntas_data = data['preguntas']
print(f"Cargando {len(preguntas_data)} preguntas...")

total_preguntas = 0
total_respuestas = 0

for preg in preguntas_data:
    area = preg['area']
    asignatura_id = mapping.get(area)
    
    if asignatura_id is None:
        print(f"WARNING: No se encontro asignatura para '{area}'")
        continue
    
    # Insertar pregunta
    cur.execute("""
        INSERT INTO preguntas (asignatura_id, enunciado, dificultad, activa, explicacion)
        VALUES (%s, %s, %s, TRUE, %s)
        RETURNING id
    """, (asignatura_id, preg['enunciado'], 2, preg.get('tema', '')))
    
    pregunta_id = cur.fetchone()[0]
    total_preguntas += 1
    
    # Insertar respuestas
    alternativas = preg['alternativas']
    clave = preg['clave']
    
    orden_letras = ['A', 'B', 'C', 'D', 'E']
    
    for letra in orden_letras:
        if letra in alternativas:
            texto = alternativas[letra]
            es_correcta = (letra == clave)
            cur.execute("""
                INSERT INTO opciones (pregunta_id, texto, es_correcta, activa)
                VALUES (%s, %s, %s, TRUE)
            """, (pregunta_id, texto, es_correcta))
            total_respuestas += 1
    
    # Mostrar progreso cada 20 preguntas
    if total_preguntas % 20 == 0:
        print(f"  {total_preguntas}/{len(preguntas_data)} preguntas cargadas...")

conn.commit()

print()
print("=== RESUMEN ===")
print(f"Preguntas creadas: {total_preguntas}")
print(f"Respuestas creadas: {total_respuestas}")

# Verificar por asignatura
print()
print("=== POR ASIGNATURA ===")
cur.execute("""
    SELECT a.nombre, COUNT(p.id) 
    FROM asignaturas a 
    LEFT JOIN preguntas p ON a.id = p.asignatura_id 
    WHERE p.id IS NOT NULL 
    GROUP BY a.id, a.nombre 
    ORDER BY COUNT(p.id) DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} preguntas")

conn.close()
print()
print("OK - 100 preguntas cargadas!")