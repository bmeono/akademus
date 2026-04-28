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
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
tables = [r[0] for r in cur.fetchall()]

sql_lines = []

for table in tables:
    cur.execute(f"""
        SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = '{table}' AND table_schema = 'public'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    
    cols_def = []
    for col in columns:
        col_name, data_type, max_len, nullable, default = col
        col_def = col_name
        
        if default and 'nextval' in default.lower():
            col_def += " SERIAL"
        else:
            dt = data_type.replace("character varying", "VARCHAR").replace("timestamp without time zone", "TIMESTAMP").replace("integer", "INTEGER").replace("boolean", "BOOLEAN").replace("text", "TEXT")
            col_def += " " + dt
            if max_len:
                col_def += f"({max_len})"
            if default and 'nextval' not in default.lower():
                col_def += f" DEFAULT {default}"
            if nullable == 'NO':
                col_def += " NOT NULL"
        
        cols_def.append(col_def)
    
    create_sql = f"CREATE TABLE {table} (\n  " + ",\n  ".join(cols_def) + "\n);"
    sql_lines.append(create_sql)
    sql_lines.append("")
    
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    for row in rows:
        values = []
        for val in row:
            if val is None:
                values.append("NULL")
            elif isinstance(val, str):
                escaped = val.replace("'", "''")
                values.append(f"'{escaped}'")
            elif isinstance(val, bool):
                values.append(str(val).upper())
            elif isinstance(val, (int, float)):
                values.append(str(val))
            else:
                values.append(f"'{str(val)}'")
        sql_lines.append(f"INSERT INTO {table} VALUES ({', '.join(values)});")
    
    sql_lines.append("")

with open("akademus_backup.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(sql_lines))

print(f"Exportado: akademus_backup.sql")
conn.close()