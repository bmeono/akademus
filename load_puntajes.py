import psycopg2
import unicodedata

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()

cur.execute('DELETE FROM configuraciones_puntaje')
conn.commit()

cur.execute('SELECT id, nombre FROM grupos_academicos')
grupos_db = {unicodedata.normalize('NFKD', g[1].upper()).encode('ASCII', 'ignore').decode(): g[0] for g in cur.fetchall()}

cur.execute('SELECT id, nombre FROM asignaturas')
asignaturas_db = {unicodedata.normalize('NFKD', a[1].upper()).encode('ASCII', 'ignore').decode(): a[0] for a in cur.fetchall()}

print('Grupos:', grupos_db)
print('Asignaturas:', asignaturas_db)

configs = []

grupos_asignaturas = {
    'Verbal': {'CIENCIAS ECONOMICAS': (20,20), 'CIENCIAS SOCIALES': (20,10), 'CIENCIAS E INGENIERIAS': (20,20), 'INGENIERIAS AGROPECUARIAS': (20,20), 'CIENCIA POLITICA Y DERECHO': (20,20)},
    'Matematica': {'CIENCIAS ECONOMICAS': (20,20), 'CIENCIAS SOCIALES': (20,20), 'CIENCIAS E INGENIERIAS': (20,20), 'INGENIERIAS AGROPECUARIAS': (20,20), 'CIENCIA POLITICA Y DERECHO': (20,20)},
    'Aritmetica': {'CIENCIAS ECONOMICAS': (5,16.0012), 'CIENCIAS SOCIALES': (5,16.0012), 'CIENCIAS E INGENIERIAS': (6,22.222), 'INGENIERIAS AGROPECUARIAS': (6,22.222), 'CIENCIA POLITICA Y DERECHO': (5,16.0012)},
    'Geometria': {'CIENCIAS ECONOMICAS': (3,16.0012), 'CIENCIAS SOCIALES': (3,16.0012), 'CIENCIAS E INGENIERIAS': (6,22.222), 'INGENIERIAS AGROPECUARIAS': (6,22.222), 'CIENCIA POLITICA Y DERECHO': (3,16.0012)},
    'Algebra': {'CIENCIAS ECONOMICAS': (4,16.0012), 'CIENCIAS SOCIALES': (4,16.0012), 'CIENCIAS E INGENIERIAS': (6,22.222), 'INGENIERIAS AGROPECUARIAS': (6,22.222), 'CIENCIA POLITICA Y DERECHO': (4,16.0012)},
    'Trigonometria': {'CIENCIAS ECONOMICAS': (3,16.0012), 'CIENCIAS SOCIALES': (3,16.0012), 'CIENCIAS E INGENIERIAS': (6,22.222), 'INGENIERIAS AGROPECUARIAS': (6,22.222), 'CIENCIA POLITICA Y DERECHO': (3,16.0012)},
    'Lenguaje': {'CIENCIAS ECONOMICAS': (6,23.529), 'CIENCIAS SOCIALES': (6,23.529), 'CIENCIAS E INGENIERIAS': (4,17.631), 'INGENIERIAS AGROPECUARIAS': (4,17.631), 'CIENCIA POLITICA Y DERECHO': (6,23.529)},
    'Literatura': {'CIENCIAS ECONOMICAS': (6,23.529), 'CIENCIAS SOCIALES': (6,23.529), 'CIENCIAS E INGENIERIAS': (2,17.631), 'INGENIERIAS AGROPECUARIAS': (2,17.631), 'CIENCIA POLITICA Y DERECHO': (6,23.529)},
    'Psicologia': {'CIENCIAS ECONOMICAS': (3,23.529), 'CIENCIAS SOCIALES': (3,23.529), 'CIENCIAS E INGENIERIAS': (2,17.631), 'INGENIERIAS AGROPECUARIAS': (2,17.631), 'CIENCIA POLITICA Y DERECHO': (3,23.529)},
    'Educacion civica': {'CIENCIAS ECONOMICAS': (3,23.529), 'CIENCIAS SOCIALES': (3,23.529), 'CIENCIAS E INGENIERIAS': (2,17.631), 'INGENIERIAS AGROPECUARIAS': (2,17.631), 'CIENCIA POLITICA Y DERECHO': (3,23.529)},
    'Historia del Peru y Universal': {'CIENCIAS ECONOMICAS': (5,23.529), 'CIENCIAS SOCIALES': (5,23.529), 'CIENCIAS E INGENIERIAS': (2,17.631), 'INGENIERIAS AGROPECUARIAS': (2,17.631), 'CIENCIA POLITICA Y DERECHO': (5,23.529)},
    'Geografia': {'CIENCIAS ECONOMICAS': (2,23.529), 'CIENCIAS SOCIALES': (2,23.529), 'CIENCIAS E INGENIERIAS': (2,17.631), 'INGENIERIAS AGROPECUARIAS': (2,17.631), 'CIENCIA POLITICA Y DERECHO': (2,23.529)},
    'Economia': {'CIENCIAS ECONOMICAS': (5,23.529), 'CIENCIAS SOCIALES': (5,23.529), 'CIENCIAS E INGENIERIAS': (3,17.631), 'INGENIERIAS AGROPECUARIAS': (3,17.631), 'CIENCIA POLITICA Y DERECHO': (5,23.529)},
    'Filosofia': {'CIENCIAS ECONOMICAS': (4,23.529), 'CIENCIAS SOCIALES': (4,23.529), 'CIENCIAS E INGENIERIAS': (2,17.631), 'INGENIERIAS AGROPECUARIAS': (2,17.631), 'CIENCIA POLITICA Y DERECHO': (4,23.529)},
    'Fisica': {'CIENCIAS ECONOMICAS': (3,14.545), 'CIENCIAS SOCIALES': (3,14.545), 'CIENCIAS E INGENIERIAS': (6,22.222), 'INGENIERIAS AGROPECUARIAS': (6,22.222), 'CIENCIA POLITICA Y DERECHO': (3,14.545)},
    'Quimica': {'CIENCIAS ECONOMICAS': (3,14.545), 'CIENCIAS SOCIALES': (3,14.545), 'CIENCIAS E INGENIERIAS': (6,22.222), 'INGENIERIAS AGROPECUARIAS': (6,22.222), 'CIENCIA POLITICA Y DERECHO': (3,14.545)},
    'Biologia': {'CIENCIAS ECONOMICAS': (5,14.545), 'CIENCIAS SOCIALES': (5,14.545), 'CIENCIAS E INGENIERIAS': (5,13.0038), 'INGENIERIAS AGROPECUARIAS': (5,13.0038), 'CIENCIA POLITICA Y DERECHO': (5,14.545)},
}

for asig_nombre, grupos in grupos_asignaturas.items():
    asig_key = unicodedata.normalize('NFKD', asig_nombre.upper()).encode('ASCII', 'ignore').decode()
    asig_id = asignaturas_db.get(asig_key)
    if asig_id is None:
        print(f'No encontro: {asig_nombre}')
        continue
    
    for grupo_nombre, (num_preg, puntaje) in grupos.items():
        grupo_key = unicodedata.normalize('NFKD', grupo_nombre.upper()).encode('ASCII', 'ignore').decode()
        grupo_id = grupos_db.get(grupo_key)
        if grupo_id is None:
            print(f'No encontro: {grupo_nombre}')
            continue
        
        cur.execute("""
            INSERT INTO configuraciones_puntaje (grupo_academico_id, asignatura_id, numero_preguntas, puntaje_pregunta, activo)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (grupo_id, asig_id, num_preg, puntaje))
        configs.append((grupo_nombre, asig_nombre, num_preg, puntaje))

conn.commit()
print(f'Creados: {len(configs)} configs')

cur.execute("""
    SELECT g.codigo, g.nombre, COUNT(c.id), SUM(c.numero_preguntas), SUM(c.numero_preguntas * c.puntaje_pregunta)
    FROM grupos_academicos g
    LEFT JOIN configuraciones_puntaje c ON g.id = c.grupo_academico_id
    GROUP BY g.id, g.codigo, g.nombre ORDER BY g.orden
""")
print()
for r in cur.fetchall():
    print(f'  {r[0]}: {r[2]} configs, {r[3] or 0} preg, total={r[4] or 0:.2f}')

conn.close()
print('OK')