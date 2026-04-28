import re

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

# Check structure
matches = re.findall(r'INSERT INTO preguntas VALUES\s*\(([^;]+)\);', content, re.IGNORECASE | re.DOTALL)
print(f'Total preguntas inserts: {len(matches)}')

print('First pregunta:')
vals = parse_values(matches[0].strip())
print(f'  Parts count: {len(vals)}')
for i, v in enumerate(vals[:6]):
    print(f'  [{i}]: {v[:50] if len(v) > 50 else v}')

# Get Neon pregunta IDs
import psycopg2
conn = psycopg2.connect('postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require')
cur = conn.cursor()
cur.execute('SELECT id, asignatura_id, LEFT(enunciado, 50) FROM preguntas LIMIT 3')
print('\nNeon preguntas structure:')
for r in cur.fetchall():
    print(f'  ID: {r[0]}, Asig: {r[1]}, Texto: {r[2]}')