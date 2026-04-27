import psycopg2

conn = psycopg2.connect(
    host='localhost', port=5432, user='postgres',
    password='1323Bri@ncisc0', database='akademus'
)
cur = conn.cursor()

# 1. Crear tabla BLOQUES TEMÁTICOS
cur.execute("""
CREATE TABLE IF NOT EXISTS bloques_tematicos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# 2. Crear tabla AREAS
cur.execute("""
CREATE TABLE IF NOT EXISTS areas (
    id SERIAL PRIMARY KEY,
    bloque_id INTEGER REFERENCES bloques_tematicos(id),
    codigo VARCHAR(10),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# 3. Crear tabla ASIGNATURAS
cur.execute("""
CREATE TABLE IF NOT EXISTS asignaturas (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    codigo VARCHAR(20),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    imagen_url VARCHAR(500),
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# 4. Crear tabla GRUPOS ACADÉMICOS
cur.execute("""
CREATE TABLE IF NOT EXISTS grupos_academicos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# 5. Crear tabla CONFIGURACIONES_PUNTAJE
cur.execute("""
CREATE TABLE IF NOT EXISTS configuraciones_puntaje (
    id SERIAL PRIMARY KEY,
    grupo_academico_id INTEGER REFERENCES grupos_academicos(id),
    asignatura_id INTEGER REFERENCES asignaturas(id),
    numero_preguntas INTEGER DEFAULT 0,
    puntaje_pregunta DECIMAL(10,4) DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(grupo_academico_id, asignatura_id)
)
""")

conn.commit()
print("Tablas creadas correctamente")

# Verificar tablas
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%bloque%' OR table_name LIKE '%area%' OR table_name LIKE '%asignatura%' OR table_name LIKE '%grupo%' OR table_name LIKE '%puntaje%' ORDER BY table_name")
print("Tablas nuevas:", [t[0] for t in cur.fetchall()])

conn.close()