import psycopg2

src = psycopg2.connect(host="db.czhvprbxvhqpprgaiqjd.supabase.co", port=5432, user="postgres", password="1323Bri@ncisc0", database="postgres")
dst = psycopg2.connect("postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require")

c_src = src.cursor()
c_dst = dst.cursor()

# Migrate usuarios first
print("Migrating usuarios...")
c_src.execute("SELECT * FROM usuarios")
rows = c_src.fetchall()

for row in rows:
    print(f"Inserting {row}")
    c_dst.execute("INSERT INTO usuarios (id, nombre_completo, email, telefono, password_hash, two_factor_enabled, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", row)
    dst.commit()

src.close()
dst.close()
print("Listo!")