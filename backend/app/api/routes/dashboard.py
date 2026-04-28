from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from psycopg2 import connect
from typing import List
import sys

sys.path.insert(0, "C:/Users/Brian/Desktop/akademus/backend")

from app.core.config import get_settings
from app.core.security import get_current_user
from app.schemas import DashboardResumen, TemaDebilResponse, EvolucionData


settings = get_settings()
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_db_connection():
    return connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )


@router.get("/test")
async def test_endpoint():
    return {"message": "test works"}


@router.get("/resumen", response_model=DashboardResumen)
async def get_resumen(current_user: dict = Depends(get_current_user)):
    """Obtiene resumen del dashboard."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Racha de días (sesiones únicas)
    cur.execute(
        """
        SELECT DISTINCT DATE(ultima_actividad) as fecha
        FROM sesiones
        WHERE usuario_id = %s AND estado = 'activa'
        ORDER BY fecha DESC
    """,
        (user_id,),
    )
    fechas = [r[0] for r in cur.fetchall()]

    racha = 0
    if fechas:
        hoy = datetime.now().date()
        for i, fecha in enumerate(fechas):
            if fecha == hoy - timedelta(days=i):
                racha += 1
            else:
                break

    # Promedio de aciertos (últimos 30 días)
    cur.execute(
        """
        SELECT COALESCE(AVG(puntaje_total), 0)
        FROM simulacros
        WHERE usuario_id = %s 
        AND fecha_inicio > %s 
        AND estado = 'finalizado'
    """,
        (user_id, datetime.now() - timedelta(days=30)),
    )
    promedio = float(cur.fetchone()[0] or 0)

    # Total preguntas respondidas
    cur.execute(
        """
        SELECT COUNT(*) FROM respuestas_simulacro r
        JOIN simulacros s ON r.simulacro_id = s.id
        WHERE s.usuario_id = %s
    """,
        (user_id,),
    )
    total_preguntas = cur.fetchone()[0]

    # Total flashcards repasadas
    cur.execute(
        """
        SELECT COUNT(*) FROM progreso_flashcards
        WHERE usuario_id = %s AND ultima_revision IS NOT NULL
    """,
        (user_id,),
    )
    total_flashcards = cur.fetchone()[0]

    # Temas débiles (porcentaje < 60%)
    cur.execute(
        """
        SELECT t.id, t.nombre,
            CAST(SUM(CASE WHEN r.es_correcta = TRUE THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as pct
        FROM preguntas p
        JOIN temas t ON p.tema_id = t.id
        JOIN respuestas_simulacro r ON r.pregunta_id = p.id
        JOIN simulacros s ON r.simulacro_id = s.id
        WHERE s.usuario_id = %s
        GROUP BY t.id, t.nombre
        HAVING CAST(SUM(CASE WHEN r.es_correcta = TRUE THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) < 0.6
        ORDER BY pct
        LIMIT 5
    """,
        (user_id,),
    )
    temas_debiles = [
        {"tema_id": r[0], "nombre": r[1], "porcentaje": round(r[2], 1)}
        for r in cur.fetchall()
    ]

    conn.close()

    return DashboardResumen(
        racha_dias=racha,
        promedio_aciertos=round(promedio, 1),
        total_preguntas_respondidas=total_preguntas,
        total_flashcards_repasadas=total_flashcards,
        temas_debiles=temas_debiles,
    )


@router.get("/evolucion", response_model=List[EvolucionData])
async def get_evolucion(current_user: dict = Depends(get_current_user)):
    """Datos para gráfico de evolución."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Últimas 8 semanas
    cur.execute(
        """
        SELECT 
            DATE_TRUNC('week', fecha_inicio)::date as semana,
            AVG(puntaje_total)
        FROM simulacros
        WHERE usuario_id = %s 
        AND fecha_inicio > %s
        AND estado = 'finalizado'
        GROUP BY DATE_TRUNC('week', fecha_inicio)
        ORDER BY semana DESC
        LIMIT 8
    """,
        (user_id, datetime.now() - timedelta(days=56)),
    )

    rows = cur.fetchall()
    conn.close()

    return [
        EvolucionData(semana=r[0].isoformat(), promedio_aciertos=round(r[1], 1))
        for r in rows
    ]


@router.get("/temas-debiles", response_model=List[TemaDebilResponse])
async def get_temas_debiles(current_user: dict = Depends(get_current_user)):
    """Lista temas con bajo rendimiento."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT t.id, t.nombre,
            CAST(SUM(CASE WHEN r.es_correcta = TRUE THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as pct
        FROM preguntas p
        JOIN temas t ON p.tema_id = t.id
        JOIN respuestas_simulacro r ON r.pregunta_id = p.id
        JOIN simulacros s ON r.simulacro_id = s.id
        WHERE s.usuario_id = %s
        GROUP BY t.id, t.nombre
        ORDER BY pct
        LIMIT 10
    """,
        (user_id,),
    )

    rows = cur.fetchall()
    conn.close()

    return [
        TemaDebilResponse(tema_id=r[0], nombre=r[1], porcentaje_aciertos=round(r[2], 1))
        for r in rows
    ]


@router.get("/estadisticas-usuario")
async def get_estadisticas_usuario(current_user: dict = Depends(get_current_user)):
    """Obtiene estadísticas del usuario: max/min puntaje y simulacros."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Obtener max/min puntaje
    cur.execute("""
        SELECT max_puntaje, min_puntaje FROM usuarios WHERE id = %s
    """, (user_id,))
    stats = cur.fetchone()

    # Obtener total de simulacros
    cur.execute("""
        SELECT COUNT(*) FROM simulacros WHERE usuario_id = %s AND estado = 'finalizado'
    """, (user_id,))
    total_simulacros = cur.fetchone()[0]

    # Obtener último puntaje
    cur.execute("""
        SELECT puntaje_total FROM simulacros 
        WHERE usuario_id = %s AND estado = 'finalizado'
        ORDER BY fecha_inicio DESC LIMIT 1
    """, (user_id,))
    ultimo = cur.fetchone()

    conn.close()

    return {
        "max_puntaje": float(stats[0]) if stats[0] else None,
        "min_puntaje": float(stats[1]) if stats[1] else None,
        "total_simulacros": total_simulacros,
        "ultimo_puntaje": float(ultimo[0]) if ultimo else None,
    }


@router.get("/temas-debiles-detalle")
async def get_temas_debiles_detalle(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT a.id, a.nombre, COUNT(rd.pregunta_id), COUNT(DISTINCT rd.pregunta_id)
        FROM resultados_detalle rd
        JOIN simulacros s ON s.id = rd.simulacro_id
        JOIN preguntas p ON p.id = rd.pregunta_id
        JOIN asignaturas a ON a.id = p.asignatura_id
        WHERE s.usuario_id = %s AND rd.es_correcta = FALSE
        GROUP BY a.id, a.nombre
        ORDER BY COUNT(rd.pregunta_id) DESC
    """, (user_id,))

    rows = cur.fetchall()
    asignaturas = [{"asignatura_id": r[0], "asignatura_nombre": r[1], "total_errores": r[2], "preguntas_falladas": r[3]} for r in rows]
    conn.close()
    return {"asignaturas": asignaturas}


@router.get("/temas-debiles/{asignatura_id}/preguntas")
async def get_preguntas_falladas(asignatura_id: int, current_user: dict = Depends(get_current_user)):
    """Obtiene las preguntas falladas de una asignatura."""
    user_id = current_user["id"]
    
    conn = get_db_connection()
    cur = conn.cursor()

    # Optimized: use JOINs instead of subqueries
    cur.execute("""
        SELECT DISTINCT ON (p.id)
            p.id as pregunta_id,
            p.enunciado,
            rd.opcion_seleccionada_id,
            os.texto as opcion_seleccionada,
            oc.texto as opcion_correcta,
            a.nombre as asignatura_nombre
        FROM resultados_detalle rd
        JOIN simulacros s ON s.id = rd.simulacro_id
        JOIN preguntas p ON p.id = rd.pregunta_id
        JOIN asignaturas a ON a.id = p.asignatura_id
        LEFT JOIN opciones os ON os.id = rd.opcion_seleccionada_id
        LEFT JOIN opciones oc ON oc.pregunta_id = p.id AND oc.es_correcta = TRUE
        WHERE s.usuario_id = %s 
            AND p.asignatura_id = %s 
            AND rd.es_correcta = FALSE
        ORDER BY p.id, rd.id
    """, (user_id, asignatura_id))

    rows = cur.fetchall()
    preguntas = []
    for r in rows:
        preguntas.append({
            "pregunta_id": r[0],
            "enunciado": r[1],
            "opcion_seleccionada_id": r[2],
            "opcion_seleccionada": r[3],
            "opcion_correcta": r[4],
            "asignatura_nombre": r[5],
        })

    conn.close()
    return preguntas


@router.get("/ultimo-simulacro")
async def get_ultimo_simulacro(current_user: dict = Depends(get_current_user)):
    """Obtiene los resultados del último simulacro para el gráfico de pastel."""
    user_id = current_user["id"]
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id FROM simulacros 
        WHERE usuario_id = %s AND estado = 'finalizado'
        ORDER BY fecha_inicio DESC
        LIMIT 1
    """, (user_id,))
    
    row = cur.fetchone()
    if not row:
        return {"total": 0, "buenas": 0, "malas": 0, "no_respondidas": 0}
    
    simulacro_id = row[0]
    
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN es_correcta = TRUE THEN 1 ELSE 0 END) as buenas,
            SUM(CASE WHEN es_correcta = FALSE AND opcion_seleccionada_id IS NOT NULL THEN 1 ELSE 0 END) as malas,
            SUM(CASE WHEN opcion_seleccionada_id IS NULL THEN 1 ELSE 0 END) as no_respondidas
        FROM resultados_detalle
        WHERE simulacro_id = %s
    """, (simulacro_id,))
    
    row = cur.fetchone()
    conn.close()
    
    return {
        "total": row[0] or 0,
        "buenas": row[1] or 0,
        "malas": row[2] or 0,
        "no_respondidas": row[3] or 0,
    }
