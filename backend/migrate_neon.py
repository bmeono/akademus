import psycopg2

# Destination - Neon
NEON = "postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Source - Supabase
SUPABASE = {
    "host": "db.czhvprbxvhqpprgaiqjd.supabase.co",
    "port": 5432,
    "user": "postgres",
    "password": "1323Bri@ncisc0",
    "database": "postgres"
}

src = psycopg2.connect(**SUPABASE)
dst = psycopg2.connect(NEON)

c_src = src.cursor()
c_dst = dst.cursor()

# Get tables
c_src.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = [r[0] for r in c_src.fetchall()]
print(f"Tablas: {tables}")

for table in tables:
    print(f"Migrando {table}...", end=" ")
    c_src.execute(f"SELECT * FROM {table}")
    rows = c_src.fetchall()
    
    if rows:
        for row in rows:
            try:
                c_dst.execute(f"INSERT INTO {table} VALUES ({','.join(['%s']*len(row))})", row)
                dst.commit()
            except:
                dst.rollback()
    print(f"{len(rows)} rows")

src.close()
dst.close()
print("Listo!")