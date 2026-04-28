import psycopg2

conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()

# Check permissions for admin
admin_id = '00e7663f-eee1-4728-ac53-d4527e91d411'
print(f"=== Permisos para admin {admin_id} ===")
cur.execute("""
    SELECT seccion, tiene_acceso 
    FROM usuario_permisos 
    WHERE usuario_id = %s
""", (admin_id,))
perms = cur.fetchall()
if perms:
    for p in perms:
        print(f"  {p[0]}: {p[1]}")
else:
    print("  NO HAY PERMISOS!")

# Check if table exists
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'usuario_permisos'
    )
""")
exists = cur.fetchone()[0]
print(f"\nTabla existe: {exists}")

# List all users with permissions
print(f"\n=== Usuarios con permisos ===")
cur.execute("SELECT DISTINCT usuario_id FROM usuario_permisos")
for u in cur.fetchall():
    print(f"  {u[0]}")

conn.close()