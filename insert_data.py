import psycopg2

conn = psycopg2.connect(
    host='localhost', port=5432, user='postgres',
    password='1323Bri@ncisc0', database='akademus'
)
cur = conn.cursor()

# primero limpiar tablas
cur.execute("TRUNCATE configuraciones_puntaje CASCADE")
cur.execute("TRUNCATE asignaturas CASCADE")
cur.execute("TRUNCATE areas CASCADE")
cur.execute("TRUNCATE bloques_tematicos CASCADE")
cur.execute("TRUNCATE grupos_academicos CASCADE")
conn.commit()

# 1. INSERTAR BLOQUES TEMÁTICOS
cur.execute("INSERT INTO bloques_tematicos (codigo, nombre, descripcion, orden) VALUES ('I', 'Bloque I', 'Habilidades y competencias básicas', 1) RETURNING id")
bloque1_id = cur.fetchone()[0]
cur.execute("INSERT INTO bloques_tematicos (codigo, nombre, descripcion, orden) VALUES ('II', 'Bloque II', 'Áreas disciplinares', 2) RETURNING id")
bloque2_id = cur.fetchone()[0]
print(f"Bloques: I={bloque1_id}, II={bloque2_id}")

# 2. INSERTAR ÁREAS (todas van al bloque II)
cur.execute("INSERT INTO areas (bloque_id, codigo, nombre, descripcion, orden) VALUES (%s, 'HAB', 'Habilidades', 'Habilidades Verbales y Matemáticas', 1) RETURNING id", (bloque2_id,))
area_hab = cur.fetchone()[0]
cur.execute("INSERT INTO areas (bloque_id, codigo, nombre, descripcion, orden) VALUES (%s, 'MAT', 'Matemática', 'Matemática', 2) RETURNING id", (bloque2_id,))
area_mat = cur.fetchone()[0]
cur.execute("INSERT INTO areas (bloque_id, codigo, nombre, descripcion, orden) VALUES (%s, 'CSH', 'Ciencias Sociales y Humanidades', 'Ciencias Sociales y Humanidades', 3) RETURNING id", (bloque2_id,))
area_csh = cur.fetchone()[0]
cur.execute("INSERT INTO areas (bloque_id, codigo, nombre, descripcion, orden) VALUES (%s, 'CYT', 'Ciencia y Tecnologia', 'Ciencia y Tecnología', 4) RETURNING id", (bloque2_id,))
area_cyt = cur.fetchone()[0]

print(f"Áreas: HAB={area_hab}, MAT={area_mat}, CSH={area_csh}, CYT={area_cyt}")

# 3. INSERTAR ASIGNATURAS
# Habilidades
for nom in ['Verbal', 'Matemática']:
    cur.execute("INSERT INTO asignaturas (area_id, nombre, descripcion, orden) VALUES (%s, %s, %s, %s)", (area_hab, nom, nom, 0))

for nom, orden in [('Aritmética', 1), ('Geometría', 2), ('Álgebra', 3), ('Trigonometría', 4)]:
    cur.execute("INSERT INTO asignaturas (area_id, nombre, descripcion, orden) VALUES (%s, %s, %s, %s)", (area_mat, nom, nom, orden))

for nom, orden in [('Lenguaje', 1), ('Literatura', 2), ('Psicología', 3), ('Educación cívica', 4), ('Historia del Perú y Universal', 5), ('Geografía', 6), ('Economía', 7), ('Filosofía', 8)]:
    cur.execute("INSERT INTO asignaturas (area_id, nombre, descripcion, orden) VALUES (%s, %s, %s, %s)", (area_csh, nom, nom, orden))

for nom, orden in [('Física', 1), ('Química', 2), ('Biología', 3)]:
    cur.execute("INSERT INTO asignaturas (area_id, nombre, descripcion, orden) VALUES (%s, %s, %s, %s)", (area_cyt, nom, nom, orden))

# 4. INSERTAR GRUPOS ACADÉMICOS
grupos = [
    ('CE', 'CIENCIAS ECONÓMICAS', 'Carreras de economía, administración y negocios', 1),
    ('CM', 'CIENCIAS MÉDICAS', 'Carreras de medicina y salud', 2),
    ('CI', 'CIENCIAS E INGENIERÍAS', 'Carreras de ingeniería', 3),
    ('IA', 'INGENIERÍAS AGROPECUARIAS', 'Carreras agrícolas y pecuarias', 4),
    ('CS', 'CIENCIAS SOCIALES', 'Carreras sociales y humanas', 5),
    ('CP', 'CIENCIA POLÍTICA Y DERECHO', 'Carreras de derecho y ciencia política', 6)
]
for cod, nom, desc, ord in grupos:
    cur.execute("INSERT INTO grupos_academicos (codigo, nombre, descripcion, orden) VALUES (%s, %s, %s, %s)", (cod, nom, desc, ord))

conn.commit()

# Obtener IDs
cur.execute("SELECT id, nombre FROM asignaturas ORDER BY id")
asign_dict = {row[1]: row[0] for row in cur.fetchall()}
cur.execute("SELECT id, codigo FROM grupos_academicos ORDER BY id")
grupos_dict = {row[1]: row[0] for row in cur.fetchall()}

print("Asignaturas:", asign_dict)
print("Grupos:", grupos_dict)

# 5. CONFIGURACIONES PUNTAJE - CIENCIAS MÉDICAS
cm_ga = grupos_dict['CM']
configs_cm = [
    ('Verbal', 20, 20.0000),
    ('Matemática', 20, 20.0000),
    ('Aritmética', 3, 14.3014),
    ('Geometría', 2, 14.3014),
    ('Álgebra', 3, 14.3014),
    ('Trigonometría', 2, 14.3014),
    ('Lenguaje', 3, 14.2770),
    ('Literatura', 2, 14.2770),
    ('Psicología', 3, 14.2770),
    ('Educación cívica', 2, 14.2770),
    ('Historia del Perú y Universal', 2, 14.2770),
    ('Geografía', 2, 14.2770),
    ('Economía', 2, 14.2770),
    ('Filosofía', 2, 14.2770),
    ('Física', 6, 25.0000),
    ('Química', 8, 25.0000),
    ('Biología', 18, 25.0000)
]
for asig_nom, num_p, punt_p in configs_cm:
    asig_id = asign_dict.get(asig_nom)
    if asig_id:
        cur.execute("INSERT INTO configuraciones_puntaje (grupo_academico_id, asignatura_id, numero_preguntas, puntaje_pregunta) VALUES (%s, %s, %s, %s)", 
                  (cm_ga, asig_id, num_p, punt_p))

conn.commit()

# Mostrar datos
print("\n=== BLOQUES ===")
cur.execute("SELECT id, codigo, nombre FROM bloques_tematicos ORDER BY orden")
for r in cur.fetchall(): print(r)

print("\n=== ÁREAS ===")
cur.execute("SELECT id, nombre FROM areas ORDER BY id")
for r in cur.fetchall(): print(r)

print("\n=== ASIGNATURAS ===")
cur.execute("SELECT id, nombre FROM asignaturas ORDER BY id")
for r in cur.fetchall(): print(r)

print("\n=== GRUPOS ACADÉMICOS ===")
cur.execute("SELECT id, codigo, nombre FROM grupos_academicos ORDER BY orden")
for r in cur.fetchall(): print(r)

print("\n=== CONFIGURACIONES PUNTAJE (CM) ===")
cur.execute("SELECT cp.numero_preguntas, cp.puntaje_pregunta, a.nombre FROM configuraciones_puntaje cp JOIN asignaturas a ON cp.asignatura_id = a.id WHERE cp.grupo_academico_id = %s", (cm_ga,))
for r in cur.fetchall(): print(f"  {r[2]}: {r[0]} preguntas x {r[1]} pts")

conn.close()
print("\n✓ Datos insertados correctamente")