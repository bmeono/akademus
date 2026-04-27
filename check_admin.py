import psycopg2
import hashlib

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()
cur.execute("SELECT email, password_hash FROM usuarios WHERE email = 'admin@akademus.com'")
result = cur.fetchone()
if result:
    print(f"Email: {result[0]}")
    print(f"Hash: {result[1]}")
    test_hash = hashlib.sha256("admin123".encode()).hexdigest()
    print(f"Test hash: {test_hash}")
    print(f"Match: {result[1] == test_hash}")
else:
    print("No se encontro admin")
conn.close()