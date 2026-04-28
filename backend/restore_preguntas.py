import psycopg2
import sys
sys.path.insert(0, "C:/Users/Brian/Desktop/akademus/backend")

from app.core.config import get_settings
settings = get_settings()

conn_local = psycopg2.connect(
    host=settings.db_host,
    port=settings.db_port,
    user=settings.db_user,
    password=settings.db_password,
    database=settings.db_name
)

conn_supabase = psycopg2.connect(
    host="db.czhvprbxvhqpprgaiqjd.supabase.co",
    port=5432,
    user="postgres",
    password="1323Bri@ncisc0",
    database="postgres"
)

cur_local = conn_local.cursor()
cur_supabase = conn_supabase.cursor()

# Get table schema from local
cur_local.execute("""
    SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = 'preguntas' AND table_schema = 'public'
    ORDER BY ordinal_position
""")
columns = cur_local.fetchall()

cols_def = []
for col_name, data_type, max_len, nullable, default in columns:
    col_def = col_name
    if default and 'nextval' in str(default).lower():
        col_def += " SERIAL"
    else:
        dt = data_type.replace("character varying", "VARCHAR").replace("timestamp without time zone", "TIMESTAMP").replace("integer", "INTEGER").replace("boolean", "BOOLEAN").replace("text", "TEXT")
        col_def += " " + dt
        if max_len:
            col_def += f"({max_len})"
        if default and 'nextval' not in str(default).lower():
            col_def += f" DEFAULT {default}"
        if nullable == 'NO':
            col_def += " NOT NULL"
    cols_def.append(col_def)

create_sql = "CREATE TABLE preguntas (\n  " + ",\n  ".join(cols_def) + "\n);"

# Drop and recreate in Supabase
cur_supabase.execute("DROP TABLE IF EXISTS preguntas CASCADE")
conn_supabase.commit()
cur_supabase.execute(create_sql)
conn_supabase.commit()
print("Tabla recreada con schema correcto")

# Insert data
cur_local.execute("SELECT * FROM preguntas")
rows = cur_local.fetchall()
print(f"Insertando {len(rows)} preguntas...")

count = 0
errors = []
for i, row in enumerate(rows):
    try:
        cur_supabase.execute("""
            INSERT INTO preguntas (id, tema_id, enunciado, explicacion, imagen_url, dificultad, activa, tipo_id, asignatura_id, usuario_id, estado, motivo_rechazo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, row)
        conn_supabase.commit()
        count += 1
    except Exception as e:
        conn_supabase.rollback()
        errors.append(str(e))

print(f"Insertadas: {count}")
if errors:
    print(f"Errores: {len(errors)}")
    for e in errors[:3]:
        print(f"  {e[:60]}")

conn_local.close()
conn_supabase.close()