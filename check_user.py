import psycopg2
import bcrypt

conn = psycopg2.connect(
    host="localhost", user="postgres", password="1323Bri@ncisc0", dbname="akademus"
)
cur = conn.cursor()

# Verificar usuario
cur.execute(
    "SELECT email, password_hash FROM usuarios WHERE email = 'test@akademus.com'"
)
user = cur.fetchone()
print("Usuario:", user[0])
print("Hash guardado:", user[1][:60])

# Verificar contraseña
password = "test123"
result = bcrypt.checkpw(password.encode("utf-8"), user[1].encode("utf-8"))
print("Password match:", result)

# Verificar activo
cur.execute("SELECT activo FROM usuarios WHERE email = 'test@akademus.com'")
print("Activo:", cur.fetchone()[0])

conn.close()
