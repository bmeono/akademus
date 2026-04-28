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
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'preguntas' AND table_schema = 'public'
    ORDER BY ordinal_position
""")
for col in cur.fetchall():
    print(col)

conn.close()

print("\n-- Supabase --\n")

conn2 = psycopg2.connect(
    host="db.czhvprbxvhqpprgaiqjd.supabase.co",
    port=5432,
    user="postgres",
    password="1323Bri@ncisc0",
    database="postgres"
)

cur2 = conn2.cursor()
cur2.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'preguntas' AND table_schema = 'public'
    ORDER BY ordinal_position
""")
for col in cur2.fetchall():
    print(col)

conn2.close()