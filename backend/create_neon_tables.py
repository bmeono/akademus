import psycopg2

# Neon connection
conn = psycopg2.connect("postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require")
cur = conn.cursor()

# Create usuarios table
cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY,
    nombre_completo VARCHAR(200),
    email VARCHAR(200) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    password_hash VARCHAR(200) NOT NULL,
    rol_id INTEGER,
    especialidad_id INTEGER,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret TEXT,
    fecha_registro TIMESTAMP,
    ultimo_login TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    max_puntaje DECIMAL,
    min_puntaje DECIMAL
)
""")
conn.commit()

# Create roles table
cur.execute("""
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    permisos JSONB
)
""")
conn.commit()

# Create areas table
cur.execute("""
CREATE TABLE IF NOT EXISTS areas (
    id SERIAL PRIMARY KEY,
    bloque_id INTEGER,
    codigo VARCHAR(10),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create asignaturas table
cur.execute("""
CREATE TABLE IF NOT EXISTS asignaturas (
    id SERIAL PRIMARY KEY,
    area_id INTEGER,
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
conn.commit()

# Create especialidades table
cur.execute("""
CREATE TABLE IF NOT EXISTS especialidades (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    grupo_academico_id INTEGER,
    codigo VARCHAR(20),
    puntaje_minimo DECIMAL,
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create preguntas table
cur.execute("""
CREATE TABLE IF NOT EXISTS preguntas (
    id SERIAL PRIMARY KEY,
    tema_id INTEGER,
    enunciado TEXT NOT NULL,
    explicacion TEXT,
    imagen_url VARCHAR(500),
    dificultad INTEGER,
    activa BOOLEAN DEFAULT TRUE,
    tipo_id INTEGER,
    asignatura_id INTEGER,
    usuario_id INTEGER,
    estado VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create opciones table
cur.execute("""
CREATE TABLE IF NOT EXISTS opciones (
    id SERIAL PRIMARY KEY,
    pregunta_id INTEGER NOT NULL,
    texto TEXT NOT NULL,
    es_correcta BOOLEAN DEFAULT FALSE,
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create simulacros table
cur.execute("""
CREATE TABLE IF NOT EXISTS simulacros (
    id SERIAL PRIMARY KEY,
    usuario_id UUID NOT NULL,
    duracion_segundos INTEGER,
    total_preguntas INTEGER,
    estado VARCHAR(20),
    grupo_academico_id INTEGER,
    especialidad_id INTEGER,
    puntaje_total DECIMAL,
    respuestas_correctas INTEGER,
    respuestas_incorrectas INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create respuestas_simulacro table
cur.execute("""
CREATE TABLE IF NOT EXISTS respuestas_simulacro (
    id SERIAL PRIMARY KEY,
    simulacro_id INTEGER NOT NULL,
    pregunta_id INTEGER NOT NULL,
    orden INTEGER NOT NULL,
    respuesta TEXT,
    puntaje DECIMAL,
    tiempo_segundos INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create resultados_detalle table
cur.execute("""
CREATE TABLE IF NOT EXISTS resultados_detalle (
    id SERIAL PRIMARY KEY,
    simulacro_id INTEGER NOT NULL,
    pregunta_id INTEGER NOT NULL,
    opcion_seleccionada_id INTEGER,
    es_correcta BOOLEAN,
    puntaje DECIMAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create flashcards table
cur.execute("""
CREATE TABLE IF NOT EXISTS flashcards (
    id SERIAL PRIMARY KEY,
    usuario_id UUID NOT NULL,
    pregunta_id INTEGER NOT NULL,
    estado VARCHAR(20) DEFAULT 'activa',
    respondida BOOLEAN DEFAULT FALSE,
    respondida_correcta BOOLEAN DEFAULT FALSE,
    facilidad INTEGER DEFAULT 2500,
    intervalo INTEGER DEFAULT 1,
    repeticiones INTEGER DEFAULT 0,
    proxima_revision DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, pregunta_id)
)
""")
conn.commit()

# Create usuario_permisos table
cur.execute("""
CREATE TABLE IF NOT EXISTS usuario_permisos (
    id SERIAL PRIMARY KEY,
    usuario_id UUID NOT NULL,
    seccion VARCHAR(50) NOT NULL,
    tiene_acceso BOOLEAN DEFAULT TRUE,
    UNIQUE(usuario_id, seccion)
)
""")
conn.commit()

# Create more tables...
cur.execute("INSERT INTO roles (nombre, descripcion) VALUES ('admin', 'Administrador') ON CONFLICT DO NOTHING")
cur.execute("INSERT INTO roles (nombre, descripcion) VALUES ('user', 'Usuario regular') ON CONFLICT DO NOTHING")
conn.commit()

conn.close()
print("Tablas creadas en Neon!")