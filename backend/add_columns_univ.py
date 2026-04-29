import psycopg2

# Conexión a Neon
conn = psycopg2.connect(
    host="ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech",
    port=5432,
    user="neondb_owner",
    password="npg_uIUNP0ZR4bzO",
    dbname="neondb",
    sslmode="require"
)

cur = conn.cursor()

# 1. Agregar columnas si no existen
try:
    cur.execute("ALTER TABLE preguntas ADD COLUMN IF NOT EXISTS universidad VARCHAR(100)")
    print("OK: columna universidad creada")
except Exception as e:
    print(f"ERROR: {e}")

try:
    cur.execute("ALTER TABLE preguntas ADD COLUMN IF NOT EXISTS an_exam VARCHAR(50)")
    print("OK: columna an_exam creada")
except Exception as e:
    print(f"ERROR: {e}")

# 2. Llenar universidad con "UNPRG" en todas las preguntas que no lo tengan
cur.execute("UPDATE preguntas SET universidad = 'UNPRG' WHERE universidad IS NULL OR universidad = ''")
print(f"OK: {cur.rowcount} preguntas actualizadas con universidad='UNPRG'")

conn.commit()
cur.close()
conn.close()

print("\n¡Listo!")