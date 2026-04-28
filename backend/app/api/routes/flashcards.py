from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import connect
import sys

sys.path.insert(0, "C:/Users/Brian/Desktop/akademus/backend")

from app.core.config import get_settings
from app.core.security import get_current_user

settings = get_settings()
router = APIRouter(prefix="/flashcards", tags=["Flashcards"])


def get_db_connection():
    return connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )


def create_flashcards_tables():
    """Crea las tablas de flashcards si no existen."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Primero borrar si existe
    cur.execute("DROP TABLE IF EXISTS flashcards CASCADE")
    cur.execute("DROP TABLE IF EXISTS flashcard_historial CASCADE")
    
    # Tabla flashcards - sin foreign keys para evitar errores
    cur.execute("""
        CREATE TABLE flashcards (
            id SERIAL PRIMARY KEY,
            usuario_id UUID NOT NULL,
            pregunta_id INTEGER NOT NULL,
            estado VARCHAR(20) DEFAULT 'activa',
            respondida BOOLEAN DEFAULT FALSE,
            respondida_correcta BOOLEAN DEFAULT FALSE,
            facilidad INTEGER DEFAULT 2500,
            intervalo INTEGER DEFAULT 1,
            repeticiones INTEGER DEFAULT 0,
            proxima_revision DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(usuario_id, pregunta_id)
        )
    """)
    
    # Tabla historial
    cur.execute("""
        CREATE TABLE flashcard_historial (
            id SERIAL PRIMARY KEY,
            flashcard_id INTEGER NOT NULL,
            usuario_id UUID NOT NULL,
            calidad_respuesta INTEGER,
            tiempo_respuesta INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


@router.get("/init")
async def init_flashcards():
    """Crea las tablas de flashcards."""
    create_flashcards_tables()
    return {"message": "flashcards table created"}


@router.get("/asignaturas")
async def get_asignaturas_con_errores(current_user: dict = Depends(get_current_user)):
    """Obtiene asignaturas con errores en simulacros."""
    user_id = current_user["id"]
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get asignaturas con preguntas falladas
        cur.execute("""
            SELECT 
                a.id as asignatura_id,
                a.nombre as asignatura_nombre,
                COUNT(rd.pregunta_id) as total_errores,
                COUNT(DISTINCT rd.pregunta_id) as preguntas_falladas
            FROM resultados_detalle rd
            JOIN simulacros s ON s.id = rd.simulacro_id
            JOIN preguntas p ON p.id = rd.pregunta_id
            JOIN asignaturas a ON a.id = p.asignatura_id
            WHERE s.usuario_id = %s AND rd.es_correcta = FALSE
            GROUP BY a.id, a.nombre
            ORDER BY total_errores DESC
            LIMIT 20
        """, (user_id,))
        
        rows = cur.fetchall()
        asignaturas = []
        for r in rows:
            asignaturas.append({
                "asignatura_id": r[0],
                "asignatura_nombre": r[1],
                "total_errores": r[2],
                "preguntas_falladas": r[3],
            })
        
        conn.close()
        return {"asignaturas": asignaturas}
    except Exception as e:
        return {"asignaturas": [], "error": str(e)}


@router.get("/asignatura/{asignatura_id}/preguntas")
async def get_preguntas_falladas_por_asignatura(asignatura_id: int, current_user: dict = Depends(get_current_user)):
    """Obtiene las preguntas falladas de una asignatura."""
    user_id = current_user["id"]
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Primero crear las flashcards para esta asignatura si no existen
        cur.execute("""
            INSERT INTO flashcards (usuario_id, pregunta_id, estado)
            SELECT %s, p.id, 'activa'
            FROM resultados_detalle rd
            JOIN simulacros s ON s.id = rd.simulacro_id
            JOIN preguntas p ON p.id = rd.pregunta_id
            WHERE s.usuario_id = %s AND p.asignatura_id = %s AND rd.es_correcta = FALSE
ON CONFLICT (usuario_id, pregunta_id) DO NOTHING
        """, (user_id, user_id, asignatura_id))
        conn.commit()
        
        # Get questions NOT answered correctly - optimized with JOINs instead of subqueries
        cur.execute("""
            SELECT DISTINCT ON (p.id)
                p.id as pregunta_id,
                p.enunciado,
                p.imagen_url,
                p.explicacion,
                oc.texto as opcion_correcta,
                oi.texto as opcion_incorrecta,
                f.id as flashcard_id,
                f.respondida,
                f.respondida_correcta
            FROM resultados_detalle rd
            JOIN simulacros s ON s.id = rd.simulacro_id
            JOIN preguntas p ON p.id = rd.pregunta_id
            LEFT JOIN opciones oc ON oc.pregunta_id = p.id AND oc.es_correcta = TRUE
            LEFT JOIN opciones oi ON oi.pregunta_id = p.id AND oi.es_correcta = FALSE AND oi.id != oc.id
            LEFT JOIN flashcards f ON f.usuario_id = %s AND f.pregunta_id = p.id
            WHERE s.usuario_id = %s 
              AND p.asignatura_id = %s 
              AND rd.es_correcta = FALSE
              AND (f.respondida IS NULL OR f.respondida_correcta = FALSE)
            ORDER BY p.id
        """, (user_id, user_id, asignatura_id))
        
        rows = cur.fetchall()
        preguntas = []
        for r in rows:
            preguntas.append({
                "pregunta_id": r[0],
                "enunciado": r[1],
                "imagen_url": r[2],
                "explicacion": r[3],
                "opcion_correcta": r[4],
                "opcion_incorrecta": r[5],
                "flashcard_id": r[6],
                "respondida": r[7],
                "respondida_correcta": r[8],
            })
        
        conn.close()
        return {"preguntas": preguntas, "total": len(preguntas)}
    except Exception as e:
        return {"preguntas": [], "error": str(e)}


@router.post("/responder")
async def responder_flashcard(data: dict, current_user: dict = Depends(get_current_user)):
    """Guarda la respuesta de una flashcard."""
    user_id = current_user["id"]
    pregunta_id = data.get("pregunta_id")
    correcta = data.get("correcta", False)
    
    if not pregunta_id:
        return {"error": "pregunta_id requerido"}
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE flashcards 
            SET respondida = TRUE, 
                respondida_correcta = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE usuario_id = %s AND pregunta_id = %s
        """, (correcta, user_id, pregunta_id))
        
        # Si no existe, crear
        if cur.rowcount == 0:
            cur.execute("""
                INSERT INTO flashcards (usuario_id, pregunta_id, respondida, respondida_correcta)
                VALUES (%s, %s, TRUE, %s)
            """, (user_id, pregunta_id, correcta))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "correcta": correcta}
    except Exception as e:
        return {"error": str(e)}


async def setup_flashcards(current_user: dict = Depends(get_current_user)):
    """Setup flashcard - crea tablas si no existen y retorna datos."""
    create_flashcards_tables()
    return await get_flashcards(current_user)


@router.get("")
async def get_flashcards(current_user: dict = Depends(get_current_user)):
    """Obtiene flashcards pendientes del usuario."""
    # Primero crear tablas
    create_flashcards_tables()
    
    user_id = current_user["id"]
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT f.id, f.pregunta_id, p.enunciado
        FROM flashcards f
        JOIN preguntas p ON p.id = f.pregunta_id
        WHERE f.usuario_id = %s AND f.estado = 'activa'
            AND f.proxima_revision <= CURRENT_DATE
        ORDER BY f.proxima_revision
        LIMIT 20
    """, (user_id,))
    
    rows = cur.fetchall()
    flashcards = []
    for r in rows:
        flashcards.append({
            "id": int(r[0]),
            "pregunta_id": int(r[1]),
            "enunciado": str(r[2]) if r[2] else "",
        })
    
    conn.close()
    return {"flashcards": flashcards}


@router.get("/progreso")
async def get_progreso(current_user: dict = Depends(get_current_user)):
    """Obtiene progreso del usuario."""
    try:
        user_id = current_user["id"]
        
        try:
            create_flashcards_tables()
        except:
            pass
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Total flashcards
        cur.execute("SELECT COUNT(*) FROM flashcards WHERE usuario_id = %s AND estado = 'activa'", (user_id,))
        total = cur.fetchone()[0]
        
        # Pendientes (para revisar hoy)
        cur.execute("""
            SELECT COUNT(*) FROM flashcards 
            WHERE usuario_id = %s AND estado = 'activa' AND proxima_revision <= CURRENT_DATE
        """, (user_id,))
        pendientes = cur.fetchone()[0]
        
        # Dominadas
        cur.execute("SELECT COUNT(*) FROM flashcards WHERE usuario_id = %s AND estado = 'dominada'", (user_id,))
        dominadas = cur.fetchone()[0]
        
        # Dominadas hoy
        cur.execute("""
            SELECT COUNT(*) FROM flashcard_historial 
            WHERE usuario_id = %s AND calidad_respuesta >= 3 AND created_at::date = CURRENT_DATE
        """, (user_id,))
        dominadas_hoy = cur.fetchone()[0]
        
        conn.close()
        
        return {
            "total": total,
            "pendientes": pendientes,
            "dominadas": dominadas,
            "dominadas_hoy": dominadas_hoy,
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/respuesta")
async def responder_flashcard(body: dict, current_user: dict = Depends(get_current_user)):
    """Registra respuesta de flashcard y calcula próxima revisión."""
    user_id = current_user["id"]
    flashcard_id = body.get("flashcard_id")
    calidad = body.get("calidad", 3)  # 0-5
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Obtener datos actuales de la flashcard
    cur.execute("""
        SELECT facilidad, intervalo, repeticiones 
        FROM flashcards WHERE id = %s AND usuario_id = %s
    """, (flashcard_id, user_id))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Flashcard no encontrada")
    
    facilidad, intervalo, repeticiones = row
    
    # Algoritmo SM-2 (SuperMemo)
    if calidad < 3:
        # Incorrecto - resetear
        nueva_facilidad = max(1300, facilidad - 200)
        nuevo_intervalo = 1
        nuevas_repeticiones = 0
    else:
        # Correcto
        nueva_facilidad = facilidad + (100 * (5 - calidad))
        nueva_facilidad = min(nueva_facilidad, 3500)
        
        nuevas_repeticiones = repeticiones + 1
        
        if nuevas_repeticiones == 1:
            nuevo_intervalo = 1
        elif nuevas_repeticiones == 2:
            nuevo_intervalo = 6
        else:
            nuevo_intervalo = int(intervalo * nueva_facilidad / 1000)
        
        # Máximo 365 días
        nuevo_intervalo = min(nuevo_intervalo, 365)
    
    # Calcular nueva fecha de revisión
    nueva_fecha = datetime.now().date() + timedelta(days=nuevo_intervalo)
    
    # Determinar estado
    estado = "activa"
    if nuevas_repeticiones >= 5 and calidad >= 4:
        estado = "dominada"
    
    # Actualizar flashcard
    cur.execute("""
        UPDATE flashcards SET 
            facilidad = %s,
            intervalo = %s,
            repeticiones = %s,
            proxima_revision = %s,
            estado = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND usuario_id = %s
    """, (nueva_facilidad, nuevo_intervalo, nuevas_repeticiones, nueva_fecha, estado, flashcard_id, user_id))
    
    # Guardar historial
    cur.execute("""
        INSERT INTO flashcard_historial (flashcard_id, usuario_id, calidad_respuesta)
        VALUES (%s, %s, %s)
    """, (flashcard_id, user_id, calidad))
    
    conn.commit()
    conn.close()
    
    return {
        "nuevo_intervalo": nuevo_intervalo,
        "repeticiones": nuevas_repeticiones,
        "estado": estado,
    }


@router.get("/historial")
async def get_historial(current_user: dict = Depends(get_current_user)):
    """Obtiene historial de repeticiones."""
    user_id = current_user["id"]
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT fh.calidad_respuesta, fh.created_at
        FROM flashcard_historial fh
        WHERE fh.usuario_id = %s
        ORDER BY fh.created_at DESC
        LIMIT 30
    """, (user_id,))
    
    rows = cur.fetchall()
    historial = [{"calidad": r[0], "fecha": r[1].isoformat()} for r in rows]
    
    conn.close()
    return {"historial": historial}