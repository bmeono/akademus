import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    from dotenv import load_dotenv
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")

print(f"Connecting to: {DATABASE_URL[:50]}...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
print("Connected!")

# Create column if not exists
try:
    cur.execute("ALTER TABLE usuarios ADD COLUMN consultas_ia_disponibles INT DEFAULT 10")
    print("Columna consultas_ia_disponibles AGREGADA")
except psycopg2.errors.DuplicateColumn:
    print("Columna consultas_ia_disponibles ya existe")
except Exception as e:
    print(f"Error columna: {e}")

# Create table
try:
    cur.execute(""""
        CREATE TABLE comunidad_consultas (
            id SERIAL PRIMARY KEY,
            usuario_id INT REFERENCES usuarios(id),
            materia VARCHAR(100),
            pregunta TEXT,
            respuesta TEXT,
            fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Tabla comunidad_consultas CREADA")
except psycopg2.errors.DuplicateTable:
    print("Tabla comunidad_consultas ya existe")
except Exception as e:
    print(f"Error tabla: {e}")

# Create index
try:
    cur.execute("CREATE INDEX idx_comunidad_usuario ON comunidad_consultas(usuario_id)")
    print("Indice CREADO")
except psycopg2.errors.DuplicateObject:
    print("Indice ya existe")
except Exception as e:
    print(f"Error indice: {e}")

conn.commit()
print("Todo listo!")

# Test
cur.execute("SELECT id, nombre FROM asignaturas LIMIT 3")
rows = cur.fetchall()
print(f"Test - asignaturas: {rows}")

conn.close()