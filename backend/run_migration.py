import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    from dotenv import load_dotenv
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Add column if not exists
try:
    cur.execute("ALTER TABLE usuarios ADD COLUMN consultas_ia_disponibles INT DEFAULT 0")
    print("Columna consultas_ia_disponibles AGREGADA")
except psycopg2.errors.DuplicateColumn:
    print("Columna consultas_ia_disponibles ya existe")

# Create table if not exists
try:
    cur.execute(""" CREATE TABLE comunidad_consultas (
        id SERIAL PRIMARY KEY,
        usuario_id INT REFERENCES usuarios(id),
        materia VARCHAR(100),
        pregunta TEXT,
        respuesta TEXT,
        fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) """)
    print("Tabla comunidad_consultas CREADA")
except psycopg2.errors.DuplicateTable:
    print("Tabla comunidad_consultas ya existe")

# Create index
try:
    cur.execute("CREATE INDEX idx_comunidad_usuario ON comunidad_consultas(usuario_id)")
    print("Indice idx_comunidad_usuario CREADO")
except psycopg2.errors.DuplicateObject:
    print("Indice idx_comunidad_usuario ya existe")

conn.commit()
conn.close()
print("Migracion completada!")