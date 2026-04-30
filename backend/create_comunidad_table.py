import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not set")
    exit(1)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    cur.execute("""CREATE TABLE IF NOT EXISTS comunidad_consultas (
        id SERIAL PRIMARY KEY,
        usuario__id INT REFERENCES usuarios(id),
        materia VARCHAR(100),
        pregunta TEXT,
        respuesta TEXT,
        fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_comunidad_consultas_usuario ON comunidad_consultas(usuario_id)")
    conn.commit()
    print("Tabla comunidad_consultas creada exitosamente")
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()