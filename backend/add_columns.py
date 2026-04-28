import psycopg2

conn = psycopg2.connect("postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require")
cur = conn.cursor()

# Add missing columns to simulacros
print("Adding fecha_inicio to simulacros...")
try:
    cur.execute("ALTER TABLE simulacros ADD COLUMN fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    conn.commit()
except:
    conn.rollback()

print("Adding fecha_fin to simulacros...")
try:
    cur.execute("ALTER TABLE simulacros ADD COLUMN fecha_fin TIMESTAMP")
    conn.commit()
except:
    conn.rollback()

print("Adding duracion_minutos to simulacros...")
try:
    cur.execute("ALTER TABLE simulacros ADD COLUMN duracion_minutos INTEGER")
    conn.commit()
except:
    conn.rollback()

# Add missing columns to usuarios
print("Adding fecha_registro to usuarios...")
try:
    cur.execute("ALTER TABLE usuarios ADD COLUMN fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    conn.commit()
except:
    conn.rollback()

try:
    cur.execute("ALTER TABLE usuarios ADD COLUMN ultimo_login TIMESTAMP")
    conn.commit()
except:
    conn.rollback()

try:
    cur.execute("ALTER TABLE usuarios ADD COLUMN activo BOOLEAN DEFAULT TRUE")
    conn.commit()
except:
    conn.rollback()

try:
    cur.execute("ALTER TABLE usuarios ADD COLUMN max_puntaje DECIMAL")
    conn.commit()
except:
    conn.rollback()

try:
    cur.execute("ALTER TABLE usuarios ADD COLUMN min_puntaje DECIMAL")
    conn.commit()
except:
    conn.rollback()

conn.close()
print("Columns added!")