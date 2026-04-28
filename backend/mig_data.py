import psycopg2
from psycopg2 import sql

# Source - Supabase
src = psycopg2.connect(host="db.czhvprbxvhqpprgaiqjd.supabase.co", port=5432, user="postgres", password="1323Bri@ncisc0", database="postgres")

# Dest - Neon
dst = psycopg2.connect("postgresql://neondb_owner:npg_uIUNP0ZR4bzO@ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require")

c_src = src.cursor()
c_dst = dst.cursor()

# Migrate usuarios
print("Migrating usuarios...")
c_src.execute("SELECT id, nombre_completo, email, telefono, password_hash, rol_id, especialidad_id, two_factor_enabled, two_factor_secret, fecha_registro, ultimo_login, activo, max_puntaje, min_puntaje FROM usuarios")
rows = c_src.fetchall()
for row in rows:
    try:
        c_dst.execute("""
            INSERT INTO usuarios 
            (id, nombre_completo, email, telefono, password_hash, rol_id, especialidad_id, two_factor_enabled, two_factor_secret, fecha_registro, ultimo_login, activo, max_puntaje, min_puntaje) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, row)
        dst.commit()
    except Exception as e:
        dst.rollback()
        print(f"Error: {e}")
print(f"OK ({len(rows)} rows)")

# Migrate areas
print("Migrating areas...")
c_src.execute("SELECT id, bloque_id, codigo, nombre, descripcion, orden, activo, created_at, updated_at FROM areas")
rows = c_src.fetchall()
for row in rows:
    try:
        c_dst.execute("""
            INSERT INTO areas 
            (id, bloque_id, codigo, nombre, descripcion, orden, activo, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, row)
        dst.commit()
    except:
        dst.rollback()
print(f"OK ({len(rows)} rows)")

# Migrate asignaturas
print("Migrating asignaturas...")
c_src.execute("SELECT * FROM asignaturas")
rows = c_src.fetchall()
for row in rows:
    try:
        c_dst.execute(f"INSERT INTO asignaturas VALUES ({','.join(['%s']*len(row))})", row)
        dst.commit()
    except:
        dst.rollback()
print(f"OK ({len(rows)} rows)")

# Migrate especialidades
print("Migrating especialidades...")
c_src.execute("SELECT * FROM especialidades")
rows = c_src.fetchall()
for row in rows:
    try:
        c_dst.execute(f"INSERT INTO especialidades VALUES ({','.join(['%s']*len(row))})", row)
        dst.commit()
    except:
        dst.rollback()
print(f"OK ({len(rows)} rows)")

# Migrate preguntas
print("Migrating preguntas...")
c_src.execute("SELECT * FROM preguntas")
rows = c_src.fetchall()
for row in rows:
    try:
        c_dst.execute(f"INSERT INTO preguntas VALUES ({','.join(['%s']*len(row))})", row)
        dst.commit()
    except:
        dst.rollback()
print(f"OK ({len(rows)} rows)")

# Migrate opciones
print("Migrating opciones...")
c_src.execute("SELECT * FROM opciones")
rows = c_src.fetchall()
for row in rows:
    try:
        c_dst.execute(f"INSERT INTO opciones VALUES ({','.join(['%s']*len(row))})", row)
        dst.commit()
    except:
        dst.rollback()
print(f"OK ({len(rows)} rows)")

src.close()
dst.close()
print("MIGRACION COMPLETA!")