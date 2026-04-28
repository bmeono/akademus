import psycopg2

conn = psycopg2.connect("postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require")
cur = conn.cursor()

# Create sesiones table
cur.execute("""
CREATE TABLE IF NOT EXISTS sesiones (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(100) UNIQUE NOT NULL,
    usuario_id UUID NOT NULL,
    expira_en TIMESTAMP NOT NULL,
    estado VARCHAR(20) DEFAULT 'activa',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create codigos_otp table
cur.execute("""
CREATE TABLE IF NOT EXISTS codigos_otp (
    id SERIAL PRIMARY KEY,
    usuario_id UUID NOT NULL,
    codigo_hash VARCHAR(200) NOT NULL,
    metodo VARCHAR(20),
    expira_en TIMESTAMP NOT NULL,
    intentos INTEGER DEFAULT 0,
    usado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create auditoria_accesos table
cur.execute("""
CREATE TABLE IF NOT EXISTS auditoria_accesos (
    id SERIAL PRIMARY KEY,
    usuario_id UUID,
    evento VARCHAR(50) NOT NULL,
    detalles TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create configuraciones table
cur.execute("""
CREATE TABLE IF NOT EXISTS configuraciones (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(50) UNIQUE NOT NULL,
    valor TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create configuraciones_puntaje table
cur.execute("""
CREATE TABLE IF NOT EXISTS configuraciones_puntaje (
    id SERIAL PRIMARY KEY,
    grupo_academico_id INTEGER,
    asignatura_id INTEGER,
    numero_preguntas INTEGER,
    puntaje_pregunta DECIMAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create bloques_tematicos table
cur.execute("""
CREATE TABLE IF NOT EXISTS bloques_tematicos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create grupos_academicos table
cur.execute("""
CREATE TABLE IF NOT EXISTS grupos_academicos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create flashcard_historial table
cur.execute("""
CREATE TABLE IF NOT EXISTS flashcard_historial (
    id SERIAL PRIMARY KEY,
    flashcard_id INTEGER NOT NULL,
    usuario_id UUID NOT NULL,
    calidad_respuesta INTEGER,
    tiempo_respuesta INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create progreso_flashcards table
cur.execute("""
CREATE TABLE IF NOT EXISTS progreso_flashcards (
    id SERIAL PRIMARY KEY,
    usuario_id UUID NOT NULL,
    asignatura_id INTEGER,
    total INTEGER DEFAULT 0,
    aprendidas INTEGER DEFAULT 0,
    pendientes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create notificaciones table
cur.execute("""
CREATE TABLE IF NOT EXISTS notificaciones (
    id SERIAL PRIMARY KEY,
    usuario_id UUID NOT NULL,
    titulo VARCHAR(200),
    mensaje TEXT,
    leida BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create tipos_pregunta table
cur.execute("""
CREATE TABLE IF NOT EXISTS tipos_pregunta (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT
)
""")
conn.commit()

# Create temas table
cur.execute("""
CREATE TABLE IF NOT EXISTS temas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    curso_id INTEGER,
    dificultad_base INTEGER,
    imagen_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create cursos table
cur.execute("""
CREATE TABLE IF NOT EXISTS cursos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    orden INTEGER DEFAULT 0,
    imagen_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create grupos_especialidad table
cur.execute("""
CREATE TABLE IF NOT EXISTS grupos_especialidad (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    orden INTEGER DEFAULT 0
)
""")
conn.commit()

# Create preguntas_puntaje_grupo table
cur.execute("""
CREATE TABLE IF NOT EXISTS preguntas_puntaje_grupo (
    id SERIAL PRIMARY KEY,
    pregunta_id INTEGER NOT NULL,
    grupo_academico_id INTEGER,
    puntaje DECIMAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create revisiones_feynman table
cur.execute("""
CREATE TABLE IF NOT EXISTS revisiones_feynman (
    id SERIAL PRIMARY KEY,
    usuario_id UUID NOT NULL,
    tema_id INTEGER,
    explicacion_usuario TEXT,
    revisada BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

conn.close()
print("Más tablas creadas!")