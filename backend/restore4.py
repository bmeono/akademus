import psycopg2

conn = psycopg2.connect(
    host="db.czhvprbxvhqpprgaiqjd.supabase.co",
    port=5432,
    user="postgres",
    password="1323Bri@ncisc0",
    database="postgres"
)

with open("akademus_backup.sql", "r", encoding="utf-8") as f:
    content = f.read()

blocks = content.split("CREATE TABLE")
cur = conn.cursor()

done = ['areas', 'asignaturas', 'auditoria_accesos', 'bloques_tematicos', 'codigos_otp', 'configuraciones', 'configuraciones_puntaje', 'cursos', 'especialidades', 'flashcard_historial', 'flashcards', 'grupos_academicos', 'grupos_especialidad', 'notificaciones', 'opciones', 'preguntas_puntaje_grupo', 'progreso_flashcards', 'respuestas_simulacro']

for block in blocks:
    table_name = block.split("(")[0].strip()
    if table_name in done:
        continue
    
    print(f"Migrando: {table_name}")
    create_lines = [l for l in block.split("\n") if not l.strip().startswith("INSERT")]
    create_cmd = "CREATE TABLE " + "\n".join(create_lines).strip().rstrip(");")
    
    try:
        cur.execute("DROP TABLE IF EXISTS " + table_name + " CASCADE")
        conn.commit()
        cur.execute(create_cmd + ")")
        conn.commit()
        
        inserts = [l.strip() for l in block.split("\n") if l.strip().startswith("INSERT")]
        for ins in inserts:
            try:
                cur.execute(ins)
                conn.commit()
            except:
                conn.rollback()
        print(f"  OK")
    except Exception as e:
        print(f"  Error: {str(e)[:60]}")
        conn.rollback()

conn.close()
print("Listo!")