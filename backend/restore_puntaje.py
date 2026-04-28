import re
import psycopg2

conn = psycopg2.connect(
    'postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require'
)

with open('C:/Users/Brian/Desktop/akademus/backend/akademus_backup.sql', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

def parse_values(s):
    vals, cur, in_str = [], '', False
    str_ch = None
    for c in s:
        if not in_str and c in ("'", "'"):
            in_str = True
            str_ch = c
            cur += c
        elif in_str and c == str_ch:
            in_str = False
            str_ch = None
            cur += c
        elif not in_str and c == ',':
            vals.append(cur.strip())
            cur = ''
        else:
            cur += c
    if cur.strip():
        vals.append(cur.strip())
    return vals

cur = conn.cursor()

pattern = r'INSERT INTO configuraciones_puntaje VALUES\s*\(([^;]+)\);'
matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)

restored = 0
for match in matches:
    vals = parse_values(match.strip())
    id_val = vals[0]
    grupo_acad = vals[1]
    asig = vals[2]
    num_preg = vals[3]
    puntaje_str = vals[4].strip("'")
    try:
        puntaje_val = float(puntaje_str)
    except:
        puntaje_val = 0.0
    activo = vals[5] if len(vals) > 5 else 'TRUE'

    try:
        sql = '''INSERT INTO configuraciones_puntaje (id, grupo_academico_id, asignatura_id, numero_preguntas, puntaje_pregunta, activo)
        VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING'''
        cur.execute(sql, (id_val, grupo_acad, asig, num_preg, puntaje_val, activo))
        conn.commit()
        restored += 1
    except Exception as e:
        print(f'Error: {e}')
        conn.rollback()

print(f'Restored {restored} configuraciones_puntaje')
cur.execute('SELECT COUNT(*) FROM configuraciones_puntaje')
print(f'Total: {cur.fetchone()[0]}')