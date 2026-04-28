import re
import psycopg2

conn = psycopg2.connect(
    host="ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech",
    port=5432,
    database="neondb",
    user="neondb_owner",
    password="npg_uIUNP0ZR4bzO",
    sslmode="require"
)

with open('C:/Users/Brian/Desktop/akademus/backend/akademus_backup.sql', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

def parse_values(sql_value_str):
    """Parse SQL VALUES string handling quoted strings properly"""
    values = []
    current = ""
    in_string = False
    string_char = None
    
    for char in sql_value_str:
        if not in_string and char in ("'", "'"):
            in_string = True
            string_char = char
            current += char
        elif in_string and char == string_char:
            # Check for escaped quote
            in_string = False
            string_char = None
            current += char
        elif not in_string and char == ',':
            values.append(current.strip())
            current = ""
        else:
            current += char
    
    if current.strip():
        values.append(current.strip())
    
    return values

# Restore especialidades
cur = conn.cursor()
pattern = r"INSERT INTO especialidades VALUES\s*\(([^;]+)\);"
matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)

restored = 0
for match in matches:
    try:
        values = parse_values(match.strip())
        # Backup: id, grupo_id, nombre, puntaje_minimo, orden, grupo_academico_id, codigo
        # Neon: id, codigo, nombre, puntaje_minimo, orden, grupo_academico_id, activo
        id_val = values[0]
        codigo = values[6].strip("'") if len(values) > 6 else "NULL"
        nombre = values[2].strip("'")
        puntaje = values[3]
        orden = values[4]
        grupo_acad = values[5] if len(values) > 5 else "NULL"

        sql = """INSERT INTO especialidades (id, codigo, nombre, puntaje_minimo, orden, grupo_academico_id, activo)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        ON CONFLICT (id) DO NOTHING"""
        cur.execute(sql, (id_val, codigo, nombre, puntaje, orden, grupo_acad))
        conn.commit()
        restored += 1
    except Exception as e:
        print(f"Error especialidades: {e}")
        conn.rollback()

print(f"Restored {restored} especialidades")

# Restore grupos_academicos
cur = conn.cursor()
pattern = r"INSERT INTO grupos_academicos VALUES\s*\(([^;]+)\);"
matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)

restored = 0
for match in matches:
    try:
        values = parse_values(match.strip())
        # Backup: id, codigo, nombre, descripcion, orden, activo, created_at, updated_at
        id_val = values[0]
        codigo = values[1].strip("'") if len(values) > 1 else "NULL"
        nombre = values[2].strip("'") if len(values) > 2 else "NULL"
        descripcion = values[3].strip("'") if len(values) > 3 and values[3].strip() not in ("NULL", "") else None
        orden = values[4] if len(values) > 4 else "1"
        activo = values[5] if len(values) > 5 else "TRUE"

        sql = """INSERT INTO grupos_academicos (id, codigo, nombre, descripcion, orden, activo)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING"""
        cur.execute(sql, (id_val, codigo, nombre, descripcion, orden, activo))
        conn.commit()
        restored += 1
    except Exception as e:
        print(f"Error grupos: {e}")
        conn.rollback()

print(f"Restored {restored} grupos_academicos")

# Verify counts
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM especialidades")
print(f"Total especialidades: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM grupos_academicos")
print(f"Total grupos_academicos: {cur.fetchone()[0]}")