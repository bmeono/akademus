import psycopg2

conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()

admin_id = '00e7663f-eee1-4728-ac53-d4527e91d411'

# Insert admin permissions
permisos = [
    ('dashboard', True),
    ('simulacros', True),
    ('temas_debiles', True),
    ('flashcards', True),
    ('feynman', True),
    ('admin', True),
]

print("=== Agregando permisos para admin ===")
for seccion, acceso in permisos:
    cur.execute("""
        INSERT INTO usuario_permisos (usuario_id, seccion, tiene_acceso)
        VALUES (%s, %s, %s)
        ON CONFLICT (usuario_id, seccion) DO UPDATE SET tiene_acceso = %s
    """, (admin_id, seccion, acceso, acceso))
    print(f"  {seccion}: {acceso}")

conn.commit()

# Verify
print("\n=== Permisos del admin ===")
cur.execute("SELECT seccion, tiene_acceso FROM usuario_permisos WHERE usuario_id = %s", (admin_id,))
for p in cur.fetchall():
    print(f"  {p[0]}: {p[1]}")

conn.close()
print("\nListo!")