import psycopg2

conn = psycopg2.connect(
    host="localhost", user="postgres", password="1323Bri@ncisc0", dbname="akademus"
)
cur = conn.cursor()

# 1. Tipos de pregunta
cur.execute("""
CREATE TABLE IF NOT EXISTS tipos_pregunta (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    icon VARCHAR(50),
    color VARCHAR(20)
)
""")

# Insertar tipos
cur.execute("""
INSERT INTO tipos_pregunta (nombre, descripcion, icon, color) VALUES 
('Alternativa múltiple', 'Seleccionar una opción correcta', 'check-circle', '#3B82F6'),
('Verdadero/Falso', 'Seleccionar verdadero o falso', 'toggle-right', '#10B981'),
('Completar', 'Completar la respuesta', 'edit', '#F59E0B'),
('Asociación', 'Relacionar elementos', 'link', '#8B5CF6'),
('Ordenar', 'Ordenar secuencias', 'list-ordered', '#EC4899')
ON CONFLICT (nombre) DO NOTHING
""")

# 2. Agregar columnas
cur.execute(
    "ALTER TABLE preguntas ADD COLUMN IF NOT EXISTS tipo_id INT REFERENCES tipos_pregunta(id)"
)
cur.execute("ALTER TABLE cursos ADD COLUMN IF NOT EXISTS imagen_url VARCHAR(500)")
cur.execute("ALTER TABLE cursos ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE")
cur.execute("ALTER TABLE temas ADD COLUMN IF NOT EXISTS imagen_url VARCHAR(500)")
cur.execute("ALTER TABLE temas ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE")

# 3. Configuraciones
cur.execute("""
CREATE TABLE IF NOT EXISTS configuraciones (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT,
    descripcion TEXT
)
""")

cur.execute("""
INSERT INTO configuraciones (clave, valor, descripcion) VALUES 
('tiempo_default_minutos', '30', 'Tiempo por defecto para simulacros'),
('preguntas_default', '10', 'Número de preguntas por defecto'),
('puntaje_aprobacion', '70', 'Puntaje mínimo para aprobar')
ON CONFLICT (clave) DO NOTHING
""")

conn.commit()
print("Tablas básicas creadas")
conn.close()
