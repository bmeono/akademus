import psycopg2
import sqlite3
from app.core.security import get_db_connection

# Conexión a Supabase (producción)
supabase_conn = psycopg2.connect(
    host="db.czhvprbxvhqpprgaiqjd.supabase.co",
    port=5432,
    user="postgres",
    password="1323Bri@ncisc0",
    database="postgres"
)

# Conexión a SQLite (local)
local_conn = sqlite3.connect("akademus.db")
local_cur = local_conn.cursor()

# Obtener tablas locales
local_cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
local_tables = [r[0] for r in local_cur.fetchall()]

print(f"Tablas a migrar: {len(local_tables)}")
print("-" * 40)

# Obtener schema y datos de cada tabla
for table in local_tables:
    local_cur.execute(f"SELECT * FROM {table}")
    columns = [desc[0] for desc in local_cur.description]
    rows = local_cur.fetchall()
    print(f"{table}: {len(rows)} filas, {len(columns)} columnas")
    
    # Obtener schema CREATE TABLE
    local_cur.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}'")
    create_sql = local_cur.fetchone()[0]
    print(f"  CREATE: {create_sql[:100]}...")

supabase_conn.close()
local_conn.close()