import psycopg2
import bcrypt

password = '2026$$Bri@n'
hash_nuevo = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
print(f"Nuevo hash: {hash_nuevo}")

conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()
cur.execute("UPDATE usuarios SET password_hash = %s WHERE email = 'admin@akademus.com'", (hash_nuevo,))
conn.commit()
print('Password actualizado')
conn.close()