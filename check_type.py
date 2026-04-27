import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()
cur.execute("SELECT column_name, data_type, numeric_precision, numeric_scale FROM information_schema.columns WHERE table_name = 'configuraciones_puntaje' AND column_name = 'puntaje_pregunta'")
result = cur.fetchone()
print(f"Column: {result[0]}, Type: {result[1]}, Precision: {result[2]}, Scale: {result[3]}")
conn.close()