import re

with open('C:/Users/Brian/Desktop/akademus/backend/akademus_backup.sql', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Count INSERT statements
preg_count = len(re.findall(r'INSERT INTO preguntas VALUES', content, re.IGNORECASE))
opc_count = len(re.findall(r'INSERT INTO opciones VALUES', content, re.IGNORECASE))

print(f'Preguntas in backup: {preg_count}')
print(f'Opciones in backup: {opc_count}')

# Get pregunta IDs from preguntas inserts
preg_matches = re.findall(r'INSERT INTO preguntas VALUES\s*\(([^;]+)\);', content, re.IGNORECASE | re.DOTALL)
preg_ids_in_preg = set()
for m in preg_matches:
    parts = m.split(',')
    if parts:
        try:
            pid = int(parts[0].strip().strip("'"))
            preg_ids_in_preg.add(pid)
        except:
            pass

print(f'Pregunta IDs from preguntas table: {len(preg_ids_in_preg)}')

# Get unique pregunta_ids from opciones
opc_matches = re.findall(r'INSERT INTO opciones VALUES\s*\(([^;]+)\);', content, re.IGNORECASE | re.DOTALL)
preg_ids_in_opc = set()
for m in opc_matches:
    parts = m.split(',')
    if len(parts) > 1:
        try:
            pid = int(parts[1].strip().strip("'"))
            preg_ids_in_opc.add(pid)
        except:
            pass

print(f'Unique pregunta_ids in opciones: {len(preg_ids_in_opc)}')

# Find preguntas without opciones
missing_opc = preg_ids_in_preg - preg_ids_in_opc
print(f'Preguntas without opciones in backup: {len(missing_opc)}')

if missing_opc:
    print(f'Sample missing IDs: {sorted(list(missing_opc))[:10]}')