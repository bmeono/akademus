import psycopg2
import sys
sys.path.insert(0, "C:/Users/Brian/Desktop/akademus/backend")

from app.core.config import get_settings
settings = get_settings()

conn = psycopg2.connect(
    host=settings.db_host,
    port=settings.db_port,
    user=settings.db_user,
    password=settings.db_password,
    database=settings.db_name
)

cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM preguntas")
print(f"Preguntas en local: {cur.fetchone()[0]}")

cur.execute("SELECT * FROM preguntas LIMIT 1")
row = cur.fetchone()
print(f"Primera pregunta: {row}")

conn.close()