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
    'Anatomía': None,
}

# Verificar si existe Anatomia
cur.execute("SELECT id FROM asignaturas WHERE nombre ILIKE '%anatomia%'")
result = cur.fetchone()
if result:
    mapping['Anatomía'] = result[0]
    print(f'Anatomia ya existe: id={result[0]}')
else:
    print('Anatomia no existe - se creara')

# Limpiar preguntas y opciones existentes
cur.execute('DELETE FROM opciones')
cur.execute('DELETE FROM preguntas')
conn.commit()
print('Limpiadas preguntas y opciones existentes')

# Crear Anatomia si no existe
if mapping['Anatomía'] is None:
    cur.execute("""
        INSERT INTO asignaturas (area_id, nombre, descripcion, orden, activo)
        VALUES (29, 'Anatomia', 'Anatomia Humana', 100, TRUE)
        RETURNING id
    """)
    mapping['Anatomía'] = cur.fetchone()[0]
    conn.commit()
    print(f'Creada Anatomia con id={mapping["Anatomía"]}')

conn.close()
print('Mapeo listo:', mapping)