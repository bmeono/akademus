import psycopg2

src = psycopg2.connect(host="db.czhvprbxvhqpprgaiqjd.supabase.co", port=5432, user="postgres", password="1323Bri@ncisc0", database="postgres")
dst = psycopg2.connect("postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require")

c_src = src.cursor()
c_dst = dst.cursor()

# Get table schema
c_src.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuarios' ORDER BY ordinal_position")
cols_src = [r[0] for r in c_src.fetchall()]
print(f"Source columns: {cols_src}")

c_dst.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuarios' ORDER BY ordinal_position")
cols_dst = [r[0] for r in c_dst.fetchall()]
print(f"Dest columns: {cols_dst}")

src.close()
dst.close()