import psycopg2

# Test Neon connection
print("Testing Neon...")
try:
    c = psycopg2.connect("postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require")
    print("Neon connected!")
    cur = c.cursor()
    cur.execute("SELECT 1")
    print(cur.fetchone())
    c.close()
except Exception as e:
    print(f"Neon error: {e}")

print("Testing Supabase...")
try:
    c = psycopg2.connect(host="db.czhvprbxvhqpprgaiqjd.supabase.co", port=5432, user="postgres", password="1323Bri@ncisc0", database="postgres")
    print("Supabase connected!")
    cur = c.cursor()
    cur.execute("SELECT 1")
    print(cur.fetchone())
    c.close()
except Exception as e:
    print(f"Supabase error: {e}")