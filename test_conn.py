import sys
sys.path.insert(0, "C:/Users/Brian/Desktop/akademus/backend")

from app.core.config import get_settings
from psycopg2 import connect

settings = get_settings()
print(f"DB Host: {settings.db_host}")
print(f"DB Port: {settings.db_port}")
print(f"DB User: {settings.db_user}")
print(f"DB Name: {settings.db_name}")

conn = connect(
    host=settings.db_host,
    port=settings.db_port,
    user=settings.db_user,
    password=settings.db_password,
    database=settings.db_name
)
cur = conn.cursor()
cur.execute("SELECT id, nombre, grupo_academico_id, puntaje_minimo, orden, codigo FROM especialidades ORDER BY id")
rows = cur.fetchall()
print(f"Found {len(rows)} rows")
for r in rows[:3]:
    print(f"  {r}")
conn.close()
print("Done")