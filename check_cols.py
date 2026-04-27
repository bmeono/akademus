import psycopg2
c = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus').cursor()
c.execute('SELECT column_name FROM information_schema.columns WHERE table_name = %s', ('asignaturas',))
cols = [r[0] for r in c.fetchall()]
print('Columnas en asignaturas:', cols)