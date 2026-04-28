import psycopg2

conn = psycopg2.connect(
    host='ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech',
    port=5432,
    user='neondb_owner',
    password='npg_uIUNP0ZR4bzO',
    database='neondb'
)
cur = conn.cursor()

# Add usuario_id column to resultados_detalle for faster queries
try:
    cur.execute("""
        ALTER TABLE resultados_detalle 
        ADD COLUMN IF NOT EXISTS usuario_id UUID REFERENCES usuarios(id)
    """)
    print("Added usuario_id column")
except Exception as e:
    print(f"Column may exist: {e}")

# Add index on usuario_id
try:
    cur.execute("CREATE INDEX IF NOT EXISTS idx_resultados_detalle_usuario ON resultados_detalle(usuario_id)")
    print("Added usuario_id index")
except Exception as e:
    print(f"Index may exist: {e}")

conn.commit()
conn.close()
print("Done!")