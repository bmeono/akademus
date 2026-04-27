import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()

# Cambiar tipo de columna
cur.execute('ALTER TABLE configuraciones_puntaje ALTER COLUMN puntaje_pregunta TYPE numeric(10,6)')
conn.commit()
print('Tipo cambiado a numeric(10,6)')

# Verificar
cur.execute("SELECT column_name, data_type, numeric_precision, numeric_scale FROM information_schema.columns WHERE table_name = 'configuraciones_puntaje' AND column_name = 'puntaje_pregunta'")
print(cur.fetchone())

conn.close()
print('OK')