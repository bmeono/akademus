@router.post("/run-comunidad-migration")
async def run_comunidad_migration(current_user: dict = Depends(require_role([1]))):
    """Ejecuta la migracion de comunidad (solo admins)."""
    conn = get_db_bridge_connection() if 'get_db_bridge_connection' in dir() else get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS consultas_ia_disponibles INT DEFAULT 0")
    except: pass
    try:
        cur.execute(""" CREATE TABLE IF NOT EXISTS comunidad_consultas (
            id SERIAL PRIMARY KEY, usuario_id INT REFERENCES usuarios(id),
            materia VARCHAR(100), pregunta TEXT, respuesta TEXT, fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) """)
    except: pass
    conn.commit()
    conn.close()
    return {"ok": True, "message": "Migracion completada"}
