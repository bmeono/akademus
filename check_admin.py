import psycopg2

conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()
cur.execute("SELECT id, email, password_hash, rol_id FROM usuarios WHERE email = 'admin@akademus.com'")
user = cur.fetchone()
if user:
    print(f"ID: {user[0]}")
    print(f"Email: {user[1]}")
    print(f"Hash: {user[2]}")
    print(f"Rol: {user[3]}")
else:
    print("Usuario no encontrado")
conn.close()