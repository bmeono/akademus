import psycopg2

conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()
password_hash = '$2b$12$pF.YAkK4zoqdxUiWPWuXVuZ0tMvUZpg3dS6QBZpmONA5R.tPt/P/.'
cur.execute("UPDATE usuarios SET password_hash = %s, rol_id = 1 WHERE email = 'admin@akademus.com'", (password_hash,))
conn.commit()
print('Admin actualizado: rol_id = 1, password cambiar')
conn.close()