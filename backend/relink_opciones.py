import re
import psycopg2

# Connect to Neon
conn = psycopg2.connect(
    'postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require'
)
cur = conn.cursor()

# Create mapping by enunciado (first 80 chars)
cur.execute('SELECT id, LEFT(enunciado, 80) FROM preguntas WHERE estado = %s OR estado IS NULL', ('aprobado',))
enunciado_map = {}
for r in cur.fetchall():
    key = r[1]
    if key not in enunciado_map:
        enunciado_map[key] = r[0]

print(f'Neon preguntas indexed: {len(enunciado_map)}')

# Read backup
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

# Clear existing opciones
print('Clearing existing opciones...')
cur.execute('DELETE FROM opciones')
conn.commit()

# Parse opciones
print('Processing opciones...')
opc_matches = re.findall(r'INSERT INTO opciones VALUES\s*\(([^;]+)\);', content, re.IGNORECASE | re.DOTALL)

# Parse preguntas to get enunciado for each pregunta_id
preg_matches = re.findall(r'INSERT INTO preguntas VALUES\s*\(([^;]+)\);', content, re.IGNORECASE | re.DOTALL)
preg_enunciado = {}
for m in preg_matches:
    vals = parse_values(m.strip())
    if len(vals) >= 3:
        orig_id = vals[0]
        enunciado = vals[2].strip("'")[:80] if len(vals) > 2 else ''
        preg_enunciado[orig_id] = enunciado

print(f'Preguntas in backup: {len(preg_enunciado)}')

restored = 0
for m in opc_matches:
    vals = parse_values(m.strip())
    if len(vals) < 4:
        continue

    opc_id = vals[0]
    orig_preg_id = vals[1].strip("'")
    texto = vals[2].strip("'")
    es_correcta = vals[3].strip() == 'TRUE'

    # Find enunciado for this pregunta
    if orig_preg_id not in preg_enunciado:
        continue

    enunciado_key = preg_enunciado[orig_preg_id]
    if not enunciado_key:
        continue

    # Find matching pregunta in Neon by enunciado
    if enunciado_key in enunciado_map:
        neon_preg_id = enunciado_map[enunciado_key]
        try:
            sql = '''INSERT INTO opciones (id, pregunta_id, texto, es_correcta, activa)
            VALUES (%s, %s, %s, %s, TRUE) ON CONFLICT (id) DO NOTHING'''
            cur.execute(sql, (opc_id, neon_preg_id, texto, es_correcta))
            restored += 1
        except Exception as e:
            conn.rollback()

conn.commit()
print(f'Restored {restored} opciones')

# Verify
cur.execute('SELECT COUNT(*) FROM opciones')
print(f'Total opciones: {cur.fetchone()[0]}')
cur.execute('SELECT COUNT(DISTINCT pregunta_id) FROM opciones')
print(f'Preguntas con opciones: {cur.fetchone()[0]}')