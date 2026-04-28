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

# First, get all pregunta_ids that exist in Neon
cur.execute('SELECT id FROM preguntas WHERE estado = %s OR estado IS NULL', ('aprobado',))
valid_pregs = set(str(r[0]) for r in cur.fetchall())
print(f'Preguntas validas en Neon: {len(valid_pregs)}')

# Parse opciones from backup
pattern = r'INSERT INTO opciones VALUES\s*\(([^;]+)\);'
matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)

restored = 0
skipped = 0

for match in matches:
    vals = parse_values(match.strip())
    if len(vals) < 4:
        skipped += 1
        continue

    id_val = vals[0]
    preg_id = vals[1]
    texto = vals[2].strip("'")
    es_correcta = vals[3].strip() == 'TRUE'

    if preg_id not in valid_pregs:
        skipped += 1
        continue

    try:
        sql = '''INSERT INTO opciones (id, pregunta_id, texto, es_correcta, activa)
        VALUES (%s, %s, %s, %s, TRUE) ON CONFLICT (id) DO NOTHING'''
        cur.execute(sql, (id_val, preg_id, texto, es_correcta))
        restored += 1
    except:
        skipped += 1
        conn.rollback()

conn.commit()
print(f'Restored {restored} opciones, skipped {skipped}')

cur.execute('SELECT COUNT(*) FROM opciones')
print(f'Total opciones: {cur.fetchone()[0]}')