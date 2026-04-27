import psycopg2

conn = psycopg2.connect(
    host='localhost', port=5432, user='postgres',
    password='1323Bri@ncisc0', database='akademus'
)
cur = conn.cursor()

# Limpiar tablas
cur.execute("TRUNCATE configuraciones_puntaje CASCADE")
cur.execute("TRUNCATE especialidades CASCADE")
cur.execute("TRUNCATE asignaturas CASCADE")
cur.execute("TRUNCATE areas CASCADE")
cur.execute("TRUNCATE bloques_tematicos CASCADE")
cur.execute("TRUNCATE grupos_academicos CASCADE")
conn.commit()

# 1. BLOQUES
cur.execute("INSERT INTO bloques_tematicos (codigo, nombre, descripcion, orden) VALUES ('I', 'Bloque I', 'Habilidades', 1) RETURNING id")
bloque1_id = cur.fetchone()[0]
cur.execute("INSERT INTO bloques_tematicos (codigo, nombre, descripcion, orden) VALUES ('II', 'Bloque II', 'Areas disciplinares', 2) RETURNING id")
bloque2_id = cur.fetchone()[0]
print(f"Bloques: I={bloque1_id}, II={bloque2_id}")

# 2. AREAS
cur.execute("INSERT INTO areas (bloque_id, codigo, nombre, descripcion, orden) VALUES (%s, 'HAB', 'Habilidades', 'Habilidades', 1) RETURNING id", (bloque1_id,))
area_hab = cur.fetchone()[0]
cur.execute("INSERT INTO areas (bloque_id, codigo, nombre, descripcion, orden) VALUES (%s, 'MAT', 'Matematica', 'Matematica', 2) RETURNING id", (bloque2_id,))
area_mat = cur.fetchone()[0]
cur.execute("INSERT INTO areas (bloque_id, codigo, nombre, descripcion, orden) VALUES (%s, 'CSH', 'Ciencias Sociales y Humanidades', 'Ciencias Sociales y Humanidades', 3) RETURNING id", (bloque2_id,))
area_csh = cur.fetchone()[0]
cur.execute("INSERT INTO areas (bloque_id, codigo, nombre, descripcion, orden) VALUES (%s, 'CYT', 'Ciencia y Tecnologia', 'Ciencia y Tecnologia', 4) RETURNING id", (bloque2_id,))
area_cyt = cur.fetchone()[0]
print(f"Areas: HAB={area_hab}, MAT={area_mat}, CSH={area_csh}, CYT={area_cyt}")

# 3. ASIGNATURAS
asignaturas_data = [
    (area_hab, 'Verbal', 1), (area_hab, 'Matematica', 2),
    (area_mat, 'Aritmetica', 3), (area_mat, 'Geometria', 4), (area_mat, 'Algebra', 5), (area_mat, 'Trigonometria', 6),
    (area_csh, 'Lenguaje', 7), (area_csh, 'Literatura', 8), (area_csh, 'Psicologia', 9), (area_csh, 'Educacion civica', 10),
    (area_csh, 'Historia del Peru y Universal', 11), (area_csh, 'Geografia', 12), (area_csh, 'Economia', 13), (area_csh, 'Filosofia', 14),
    (area_cyt, 'Fisica', 15), (area_cyt, 'Quimica', 16), (area_cyt, 'Biologia', 17)
]
asign_ids = {}
for area_id, nombre, orden in asignaturas_data:
    cur.execute("INSERT INTO asignaturas (area_id, nombre, descripcion, orden) VALUES (%s, %s, %s, %s) RETURNING id", (area_id, nombre, nombre, orden))
    asign_ids[nombre] = cur.fetchone()[0]
print(f"Asignaturas: {len(asign_ids)} insertadas")

# 4. GRUPOS ACADEMICOS
cur.execute("INSERT INTO grupos_academicos (codigo, nombre, descripcion, orden) VALUES ('CE', 'CIENCIAS ECONOMICAS', 'Ciencias Economicas', 1) RETURNING id")
ga_ce = cur.fetchone()[0]
cur.execute("INSERT INTO grupos_academicos (codigo, nombre, descripcion, orden) VALUES ('CM', 'CIENCIAS MEDICAS', 'Ciencias Medicas', 2) RETURNING id")
ga_cm = cur.fetchone()[0]
cur.execute("INSERT INTO grupos_academicos (codigo, nombre, descripcion, orden) VALUES ('CI', 'CIENCIAS E INGENIERIAS', 'Ciencias e Ingenierias', 3) RETURNING id")
ga_ci = cur.fetchone()[0]
cur.execute("INSERT INTO grupos_academicos (codigo, nombre, descripcion, orden) VALUES ('IA', 'INGENIERIAS AGROPECUARIAS', 'Ingenierias Agropecuarias', 4) RETURNING id")
ga_ia = cur.fetchone()[0]
cur.execute("INSERT INTO grupos_academicos (codigo, nombre, descripcion, orden) VALUES ('CS', 'CIENCIAS SOCIALES', 'Ciencias Sociales', 5) RETURNING id")
ga_cs = cur.fetchone()[0]
cur.execute("INSERT INTO grupos_academicos (codigo, nombre, descripcion, orden) VALUES ('CP', 'CIENCIA POLITICA Y DERECHO', 'Ciencia Politica y Derecho', 6) RETURNING id")
ga_cp = cur.fetchone()[0]
print(f"Grupos: CE={ga_ce}, CM={ga_cm}, CI={ga_ci}, IA={ga_ia}, CS={ga_cs}, CP={ga_cp}")

conn.commit()

# 5. ESPECIALIDADES
esp_data = [
    ('P01', 'INGENIERIA AGRICOLA', ga_ia), ('P02', 'ARQUITECTURA', ga_ci), ('P03', 'INGENIERIA CIVIL', ga_ci),
    ('P04', 'INGENIERIA DE SISTEMAS', ga_ci), ('P05', 'INGENIERIA MECANICA Y ELECTRICA', ga_ci),
    ('P06', 'INGENIERIA QUIMICA', ga_ci), ('P07', 'INGENIERIA DE INDUSTRIAS ALIMENTARIAS', ga_ci),
    ('P08', 'ENFERMERIA', ga_cm), ('P09', 'MEDICINA HUMANA', ga_cm), ('P10', 'DERECHO', ga_cp),
    ('P11', 'CIENCIA POLITICA', ga_cp), ('P12', 'ADMINISTRACION', ga_ce), ('P13', 'COMERCIO Y NEGOCIOS INTERNACIONALES', ga_ce),
    ('P14', 'CONTABILIDAD', ga_ce), ('P15', 'ECONOMIA', ga_ce), ('P16', 'INGENIERIA EN COMPUTACION E INFORMATICA', ga_ci),
    ('P17', 'ESTADISTICA', ga_ci), ('P18', 'FISICA', ga_ci), ('P19', 'MATEMATICA', ga_ci), ('P20', 'INGENIERIA ELECTRONICA', ga_ci),
    ('P21', 'ARQUEOLOGIA', ga_cs), ('P22', 'ARTE - ARTES PLASTICAS', ga_cs), ('P23', 'ARTE - TEATRO', ga_cs),
    ('P24', 'ARTE - PEDAGOGIA ARTISTICA', ga_cs), ('P25', 'ARTE - MUSICA', ga_cs), ('P26', 'ARTE - DANZAS', ga_cs),
    ('P27', 'CIENCIAS DE LA COMUNICACION', ga_cs), ('P28', 'PSICOLOGIA', ga_cs), ('P29', 'SOCIOLOGIA', ga_cs),
    ('P30', 'EDUCACION - INICIAL', ga_cs), ('P31', 'EDUCACION - PRIMARIA', ga_cs), ('P32', 'EDUCACION - CIENCIAS NATURALES', ga_cs),
    ('P33', 'EDUCACION - CIENCIAS HISTORICO SOCIALES Y FILOSOFIA', ga_cs), ('P34', 'EDUCACION - LENGUA Y LITERATURA', ga_cs),
    ('P35', 'EDUCACION - IDIOMAS EXTRANJEROS', ga_cs), ('P36', 'EDUCACION - MATEMATICA Y COMPUTACION', ga_cs),
    ('P37', 'EDUCACION - EDUCACION FISICA', ga_cs), ('P38', 'CIENCIAS BIOLOGICAS - BIOLOGIA', ga_cm),
    ('P39', 'CIENCIAS BIOLOGICAS - BOTANICA', ga_cm), ('P40', 'CIENCIAS BIOLOGICAS - MICROBIOLOGIA Y PARASITOLOGIA', ga_cm),
    ('P41', 'CIENCIAS BIOLOGICAS - PESQUERIA', ga_cm), ('P42', 'AGRONOMIA', ga_ia), ('P43', 'INGENIERIA ZOOTECNIA', ga_ia),
    ('P44', 'MEDICINA VETERINARIA', ga_cm)
]
for cod, nombre, grupo_id in esp_data:
    cur.execute("INSERT INTO especialidades (nombre, grupo_academico_id, codigo, orden) VALUES (%s, %s, %s, 0)", (nombre, grupo_id, cod))

conn.commit()
print(f"Especialidades: {len(esp_data)} insertadas")

# 6. CONFIGURACIONES PUNTAJE - CIENCIAS MEDICAS
configs_cm = [
    ('Verbal', 20, 20.0000), ('Matematica', 20, 20.0000),
    ('Aritmetica', 3, 14.3014), ('Geometria', 2, 14.3014), ('Algebra', 3, 14.3014), ('Trigonometria', 2, 14.3014),
    ('Lenguaje', 3, 14.2770), ('Literatura', 2, 14.2770), ('Psicologia', 3, 14.2770),
    ('Educacion civica', 2, 14.2770), ('Historia del Peru y Universal', 2, 14.2770),
    ('Geografia', 2, 14.2770), ('Economia', 2, 14.2770), ('Filosofia', 2, 14.2770),
    ('Fisica', 6, 25.0000), ('Quimica', 8, 25.0000), ('Biologia', 18, 25.0000)
]
for nombre, num_p, punt_p in configs_cm:
    asig_id = asign_ids.get(nombre)
    if asig_id:
        cur.execute("INSERT INTO configuraciones_puntaje (grupo_academico_id, asignatura_id, numero_preguntas, puntaje_pregunta) VALUES (%s, %s, %s, %s)", (ga_cm, asig_id, num_p, punt_p))

conn.commit()
print(f"Config Puntaje CM: {len(configs_cm)} registros")

# Verificacion
print("\n=== VERIFICACION ===")
cur.execute("SELECT COUNT(*) FROM bloques_tematicos"); print(f"Bloques: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM areas"); print(f"Areas: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM asignaturas"); print(f"Asignaturas: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM grupos_academicos"); print(f"Grupos: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM especialidades"); print(f"Especialidades: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM configuraciones_puntaje"); print(f"Config Puntaje: {cur.fetchone()[0]}")

conn.close()
print("\nDatos cargados correctamente")