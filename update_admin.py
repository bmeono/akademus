import psycopg2
import bcrypt

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()

password_hash = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
cur.execute("UPDATE usuarios SET password_hash = %s WHERE email = 'admin@akademus.com'", (password_hash,))
conn.commit()
print(f"Password updated with bcrypt")

conn.close()