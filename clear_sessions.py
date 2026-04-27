import psycopg2

conn = psycopg2.connect(
    host="localhost", user="postgres", password="1323Bri@ncisc0", dbname="akademus"
)
cur = conn.cursor()
cur.execute("DELETE FROM sesiones")
conn.commit()
print("Sesiones eliminadas")
conn.close()
