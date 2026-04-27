import psycopg2
c = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus').cursor()
c.execute("SELECT COUNT(*) FROM preguntas WHERE estado = 'pendiente'")
print('Pendientes:', c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM preguntas WHERE estado = 'aprobado'")
print('Aprobadas:', c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM preguntas WHERE estado = 'rechazado'")
print('Rechazadas:', c.fetchone()[0])