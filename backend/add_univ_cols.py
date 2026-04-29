import psycopg2
import os

# Usar variables de entorno o valores por defecto
host = os.environ.get("NEON_HOST", "ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech")
user = os.environ.get("NEON_USER", "neondb_owner")
password = os.environ.get("NEON_PASSWORD", "npg_uIUNP0ZR4bzO")
dbname = os.environ.get("NEON_DB", "neondb")

conn = psycopg2.connect(
    host=host,
    port=5432,
    user=user,
    password=password,
    dbname=dbname,
    sslmode="require"
)

cur = conn.cursor()

# 1. Agregar columnas
try:
    cur.execute("ALTER TABLE preguntas ADD COLUMN IF NOT EXISTS universidad VARCHAR(100)")
    print("OK: columna universidad creada")
except Exception as e:
    print(f"ERROR columna universidad: {e}")

try:
    cur.execute("ALTER TABLE preguntas ADD COLUMN IF NOT EXISTS an_exam VARCHAR(50)")
    print("OK: columna an_exam creada")
except Exception as e:
    print(f"ERROR columna an_exam: {e}")

# 2. Llenar universidad con UNPRG
cur.execute("UPDATE preguntas SET universidad = 'UNPRG' WHERE universidad IS NULL OR universidad = ''")
print(f"OK: {cur.rowcount} preguntas actualizadas con universidad='UNPRG'")

conn.commit()
cur.close()
conn.close()

print("\n¡Listo! Columnas agregadas correctamente.")