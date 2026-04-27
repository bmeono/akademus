import psycopg2
import hashlib

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()

password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
cur.execute("INSERT INTO usuarios (email, password_hash, rol_id, activo, nombre_completo, telefono) VALUES ('admin@akademus.com', %s, 2, true, 'Administrador', '+51999999999') ON CONFLICT (email) DO NOTHING", (password_hash,))
conn.commit()
print('Admin creado')

conn.close()