import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()
cur.execute("UPDATE usuarios SET two_factor_enabled = false WHERE email = 'admin@akademus.com'")
conn.commit()
print('2FA deshabilitado')
conn.close()