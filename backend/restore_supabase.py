import psycopg2

supabase_conn = psycopg2.connect(
    host="db.czhvprbxvhqpprgaiqjd.supabase.co",
    port=5432,
    user="postgres",
    password="1323Bri@ncisc0",
    database="postgres"
)

with open("akademus_backup.sql", "r", encoding="utf-8") as f:
    content = f.read()

blocks = content.split("CREATE TABLE")
blocks = [b.strip() for b in blocks if b.strip()]

cur = supabase_conn.cursor()
tables_ok = 0

for block in blocks:
    table_name = block.split("(")[0].strip()
    print(f"Procesando: {table_name}")
    
    # Obtener CREATE (buscar hasta el primer INSERT o fin de bloque)
    create_lines = []
    for line in block.split("\n"):
        if line.strip().startswith("INSERT"):
            break
        create_lines.append(line)
    
    create_cmd = "CREATE TABLE " + "\n".join(create_lines).strip()
    # Quitar último ) si existe
    create_cmd = create_cmd.rstrip(");")
    
    try:
        cur.execute("DROP TABLE IF EXISTS " + table_name + " CASCADE")
        supabase_conn.commit()
    except:
        pass
    
    try:
        cur.execute(create_cmd + ")")
        supabase_conn.commit()
        
        # INSERTs
        inserts = [l.strip() for l in block.split("\n") if l.strip().startswith("INSERT")]
        for ins in inserts:
            try:
                cur.execute(ins)
                supabase_conn.commit()
            except:
                supabase_conn.rollback()
        
        tables_ok += 1
        print(f"  OK")
    except Exception as e:
        print(f"  Error: {str(e)[:60]}")
        supabase_conn.rollback()

supabase_conn.close()
print(f"\n=== {tables_ok} tablas migradas ===")