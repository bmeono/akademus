import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from psycopg2 import connect
from typing import List, Optional

import sys

sys.path.insert(0, "C:/Users/Brian/Desktop/akademus/backend")

from app.core.config import get_settings
from app.core.security import get_current_user
from app.schemas import (
    SimulacroConfig,
    SimulacroEspecialidadConfig,
    SimulacroStartResponse,
    RespuestaEnviar,
    RespuestaResultResponse,
    SimulacroResultResponse,
    PreguntaCompletaResponse,
    PreguntaResponse,
    OpcionResponse,
)
from pydantic import BaseModel
from typing import List


settings = get_settings()
router = APIRouter(prefix="/simulacros", tags=["Simulacros"])


def get_db_connection():
    return connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )


@router.get("/config")
async def get_config(current_user: dict = Depends(get_current_user)):
    """Obtiene opciones para configurar simulacro."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Cursos disponibles
    cur.execute("SELECT id, nombre FROM cursos ORDER BY orden")
    cursos = [{"id": r[0], "nombre": r[1]} for r in cur.fetchall()]

    # Temas por curso
    cur.execute("SELECT id, nombre, curso_id FROM temas ORDER BY curso_id, nombre")
    temas = [{"id": r[0], "nombre": r[1], "curso_id": r[2]} for r in cur.fetchall()]

    conn.close()

    return {"cursos": cursos, "temas": temas}


@router.get("/especialidades")
async def get_especialidades(current_user: dict = Depends(get_current_user)):
    """Obtiene lista de especialidades para selector."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT e.id, e.nombre, e.grupo_academico_id, g.nombre as grupo_nombre
        FROM especialidades e 
        JOIN grupos_academicos g ON e.grupo_academico_id = g.id 
        ORDER BY g.orden, e.codigo
    """)
    especialidades = [
        {"id": r[0], "nombre": r[1], "grupo_id": r[2], "grupo_nombre": r[3]} 
        for r in cur.fetchall()
    ]
    
    conn.close()
    return especialidades


@router.post("/iniciar-por-especialidad")
async def iniciar_simulacro_especialidad(
    config: SimulacroEspecialidadConfig, current_user: dict = Depends(get_current_user)
):
    """Inicia simulacro basado en especialidad seleccionada."""
    user_id = current_user["id"]
    
    if not config.especialidad_id:
        raise HTTPException(status_code=400, detail="Se requiere seleccionar una especialidad")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Obtener grupo académico de la especialidad
    cur.execute("""
        SELECT grupo_academico_id FROM especialidades WHERE id = %s
    """, (config.especialidad_id,))
    result = cur.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="Especialidad no encontrada")
    
    grupo_id = result[0]
    
    # Obtener configuración de puntaje del grupo
    cur.execute("""
        SELECT cp.asignatura_id, cp.numero_preguntas, cp.puntaje_pregunta, a.nombre
        FROM configuraciones_puntaje cp
        JOIN asignaturas a ON cp.asignatura_id = a.id
        WHERE cp.grupo_academico_id = %s AND cp.activo = TRUE
        ORDER BY a.orden
    """, (grupo_id,))
    config_puntaje = cur.fetchall()
    
    if not config_puntaje:
        conn.close()
        raise HTTPException(status_code=400, detail="No hay configuración de puntaje para este grupo")
    
    total_preguntas = sum(row[1] for row in config_puntaje)
    
    # Seleccionar preguntas aleatorias por asignatura según distribución
    preguntas_seleccionadas = []
    puntajes_por_pregunta = {}
    
    for asignatura_id, num_preguntas, puntaje, _ in config_puntaje:
        cur.execute("""
            SELECT id FROM preguntas 
            WHERE asignatura_id = %s AND estado = 'aprobado' AND activa = TRUE
            ORDER BY RANDOM() 
            LIMIT %s
        """, (asignatura_id, num_preguntas))
        preguntas = [r[0] for r in cur.fetchall()]
        
        if len(preguntas) < num_preguntas:
            conn.close()
            raise HTTPException(
                status_code=400, 
                detail=f"No hay suficientes preguntas para {puntaje}. Necesarias: {num_preguntas}, Disponibles: {len(preguntas)}"
            )
        
        for p in preguntas:
            preguntas_seleccionadas.append(p)
            puntajes_por_pregunta[p] = puntaje
    
    # Crear simulacro (100 preguntas, 180 minutos)
    duracion_segundos = 180 * 60
    cur.execute("""
        INSERT INTO simulacros (usuario_id, duracion_segundos, total_preguntas, estado, grupo_academico_id, especialidad_id)
        VALUES (%s, %s, %s, 'en_curso', %s, %s)
        RETURNING id
    """, (user_id, duracion_segundos, total_preguntas, grupo_id, config.especialidad_id))
    simulacro_id = cur.fetchone()[0]
    
    # Guardar preguntas del simulacro con su puntaje
    for i, pregunta_id in enumerate(preguntas_seleccionadas):
        puntaje = puntajes_por_pregunta[pregunta_id]
        cur.execute("""
            INSERT INTO respuestas_simulacro (simulacro_id, pregunta_id, orden, puntaje_pregunta)
            VALUES (%s, %s, %s, %s)
        """, (simulacro_id, pregunta_id, i + 1, puntaje))
    
    conn.commit()
    conn.close()
    
    return SimulacroStartResponse(
        simulacro_id=simulacro_id,
        total_preguntas=total_preguntas,
        duracion_segundos=duracion_segundos,
    )
async def iniciar_simulacro(
    config: SimulacroConfig, current_user: dict = Depends(get_current_user)
):
    """Inicia un nuevo simulacro."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Construye query de preguntas
    if config.tema_ids:
        placeholders = ",".join(["%s"] * len(config.tema_ids))
        cur.execute(
            f"""
            SELECT id FROM preguntas 
            WHERE tema_id IN ({placeholders}) AND activa = TRUE
            ORDER BY RANDOM() 
            LIMIT {config.num_preguntas}
        """,
            tuple(config.tema_ids),
        )
    else:
        placeholders = ",".join(["%s"] * len(config.curso_ids))
        cur.execute(
            f"""
            SELECT p.id FROM preguntas p
            JOIN temas t ON p.tema_id = t.id
            WHERE t.curso_id IN ({placeholders}) AND p.activa = TRUE
            ORDER BY RANDOM() 
            LIMIT {config.num_preguntas}
        """,
            tuple(config.curso_ids),
        )

    preguntas = [r[0] for r in cur.fetchall()]

    if len(preguntas) < config.num_preguntas:
        conn.close()
        raise HTTPException(status_code=400, detail="No hay suficientes preguntas")

    # Crea simulacro
    duracion_segundos = config.duracion_minutos * 60
    cur.execute(
        """
        INSERT INTO simulacros (usuario_id, duracion_segundos, total_preguntas, estado)
        VALUES (%s, %s, %s, 'en_curso')
        RETURNING id
    """,
        (user_id, duracion_segundos, config.num_preguntas),
    )
    simulacro_id = cur.fetchone()[0]

    # Guarda preguntas del simulacro
    for i, pregunta_id in enumerate(preguntas):
        cur.execute(
            """
            INSERT INTO respuestas_simulacro (simulacro_id, pregunta_id, orden)
            VALUES (%s, %s, %s)
        """,
            (simulacro_id, pregunta_id, i + 1),
        )

    conn.commit()
    conn.close()

    return SimulacroStartResponse(
        simulacro_id=simulacro_id,
        total_preguntas=config.num_preguntas,
        duracion_segundos=duracion_segundos,
    )


@router.get("/{simulacro_id}/pregunta/{orden}", response_model=PreguntaCompletaResponse)
async def get_pregunta(
    simulacro_id: int, orden: int, current_user: dict = Depends(get_current_user)
):
    """Obtiene pregunta por orden."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Verifica simulacro pertenece al usuario
    cur.execute(
        """
        SELECT s.id FROM simulacros s 
        WHERE s.id = %s AND s.usuario_id = %s AND s.estado = 'en_curso'
    """,
        (simulacro_id, user_id),
    )
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Simulacro no encontrado")

    # Obtiene pregunta
    cur.execute(
        """
        SELECT p.id, p.tema_id, p.enunciado, p.explicacion, p.imagen_url, p.dificultad
        FROM preguntas p
        JOIN respuestas_simulacro r ON r.pregunta_id = p.id
        WHERE r.simulacro_id = %s AND r.orden = %s
    """,
        (simulacro_id, orden),
    )
    pregunta = cur.fetchone()

    if not pregunta:
        conn.close()
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")

    # Obtiene opciones
    cur.execute(
        """
        SELECT id, pregunta_id, texto FROM opciones 
        WHERE pregunta_id = %s
    """,
        (pregunta[0],),
    )
    opciones = [
        OpcionResponse(id=r[0], pregunta_id=r[1], texto=r[2]) for r in cur.fetchall()
    ]

    conn.close()

    return PreguntaCompletaResponse(
        pregunta=PreguntaResponse(
            id=pregunta[0],
            tema_id=pregunta[1],
            enunciado=pregunta[2],
            explicacion=pregunta[3],
            imagen_url=pregunta[4],
            dificultad=pregunta[5],
        ),
        opciones=opciones,
    )


@router.get("/{simulacro_id}/todas")
async def get_todas_preguntas(
    simulacro_id: int, current_user: dict = Depends(get_current_user)
):
    """Obtiene todas las preguntas del simulacro de una vez."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.id, s.duracion_segundos, s.fecha_inicio, s.total_preguntas, s.estado
        FROM simulacros s
        WHERE s.id = %s AND s.usuario_id = %s
    """, (simulacro_id, user_id))
    simulacro = cur.fetchone()

    if not simulacro:
        conn.close()
        raise HTTPException(status_code=404, detail="Simulacro no encontrado")

    duracion_segundos = simulacro[1]

    # Calcula tiempo restante
    fecha_inicio = simulacro[2]
    if fecha_inicio:
        import datetime
        ahora = datetime.datetime.now()
        elapsed = (ahora - fecha_inicio).total_seconds()
        tiempo_restante = max(0, duracion_segundos - elapsed)
    else:
        tiempo_restante = duracion_segundos

    # Obtiene todas las preguntas
    cur.execute("""
        SELECT p.id, p.enunciado, p.explicacion, p.imagen_url, p.dificultad, r.orden, r.puntaje_pregunta
        FROM preguntas p
        JOIN respuestas_simulacro r ON r.pregunta_id = p.id
        WHERE r.simulacro_id = %s
        ORDER BY r.orden
    """, (simulacro_id,))
    preguntas_raw = cur.fetchall()

    # Obtiene opciones para todas las preguntas
    pregunta_ids = [p[0] for p in preguntas_raw]
    opciones_map = {}
    if pregunta_ids:
        placeholders = ",".join(["%s"] * len(pregunta_ids))
        cur.execute(f"""
            SELECT id, pregunta_id, texto, es_correcta 
            FROM opciones 
            WHERE pregunta_id IN ({placeholders})
        """, tuple(pregunta_ids))
        for opcion in cur.fetchall():
            pid = opcion[1]
            if pid not in opciones_map:
                opciones_map[pid] = []
            opciones_map[pid].append({
                "id": opcion[0],
                "texto": opcion[2],
                "es_correcta": opcion[3]
            })

    preguntas = []
    for p in preguntas_raw:
        preguntas.append({
            "id": p[0],
            "enunciado": p[1],
            "explicacion": p[2],
            "imagen_url": p[3],
            "dificultad": p[4],
            "orden": p[5],
            "puntaje_pregunta": p[6],
            "opciones": opciones_map.get(p[0], [])
        })

    conn.close()

    return {
        "preguntas": preguntas,
        "tiempo_restante": int(tiempo_restante),
        "total_preguntas": len(preguntas)
    }


@router.post("/{simulacro_id}/responder", response_model=RespuestaResultResponse)
async def responder_pregunta(
    simulacro_id: int,
    data: RespuestaEnviar,
    current_user: dict = Depends(get_current_user),
):
    """Envia respuesta de pregunta."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Verifica simulacro
    cur.execute(
        """
        SELECT s.id, s.total_preguntas, s.fecha_inicio, s.duracion_segundos
        FROM simulacros s
        WHERE s.id = %s AND s.usuario_id = %s AND s.estado = 'en_curso'
    """,
        (simulacro_id, user_id),
    )
    simulacro = cur.fetchone()

    if not simulacro:
        conn.close()
        raise HTTPException(status_code=404, detail="Simulacro no encontrado")

    # Verifica tiempo
    tiempo_transcurrido = (datetime.utcnow() - simulacro[2]).total_seconds()
    if tiempo_transcurrido > simulacro[3]:
        cur.execute(
            "UPDATE simulacros SET estado = 'finalizado' WHERE id = %s", (simulacro_id,)
        )
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail="Tiempo agotado")

    # Verifica opción correcta
    cur.execute(
        "SELECT es_correcta FROM opciones WHERE id = %s", (data.opcion_seleccionada_id,)
    )
    opcion = cur.fetchone()

    if not opcion:
        conn.close()
        raise HTTPException(status_code=404, detail="Opción no encontrada")

    es_correcta = opcion[0]

    # Actualiza respuesta
    cur.execute(
        """
        UPDATE respuestas_simulacro 
        SET opcion_seleccionada_id = %s, tiempo_respuesta_segundos = %s, es_correcta = %s
        WHERE simulacro_id = %s AND pregunta_id = %s
    """,
        (
            data.opcion_seleccionada_id,
            data.tiempo_respuesta_segundos,
            es_correcta,
            simulacro_id,
            data.pregunta_id,
        ),
    )

    # Obtiene siguiente pregunta
    cur.execute(
        """
        SELECT COUNT(*) FROM respuestas_simulacro 
        WHERE simulacro_id = %s AND opcion_seleccionada_id IS NOT NULL
    """,
        (simulacro_id,),
    )
    respondidas = cur.fetchone()[0]

    siguiente_orden = respondidas + 1

    if siguiente_orden <= simulacro[1]:
        cur.execute(
            """
            SELECT p.id, p.tema_id, p.enunciado, p.explicacion, p.imagen_url, p.dificultad
            FROM preguntas p
            JOIN respuestas_simulacro r ON r.pregunta_id = p.id
            WHERE r.simulacro_id = %s AND r.orden = %s
        """,
            (simulacro_id, siguiente_orden),
        )
        sig_pregunta = cur.fetchone()

        if sig_pregunta:
            cur.execute(
                "SELECT id, pregunta_id, texto FROM opciones WHERE pregunta_id = %s",
                (sig_pregunta[0],),
            )
            opciones = [
                OpcionResponse(id=r[0], pregunta_id=r[1], texto=r[2])
                for r in cur.fetchall()
            ]
            siguiente = PreguntaCompletaResponse(
                pregunta=PreguntaResponse(
                    id=sig_pregunta[0],
                    tema_id=sig_pregunta[1],
                    enunciado=sig_pregunta[2],
                    explicacion=sig_pregunta[3],
                    imagen_url=sig_pregunta[4],
                    dificultad=sig_pregunta[5],
                ),
                opciones=opciones,
            )
        else:
            siguiente = None
    else:
        siguiente = None

    conn.commit()
    conn.close()

    # Obtiene explicación si falló
    explicacion = None if es_correcta else data.get("explicacion")

    return RespuestaResultResponse(
        es_correcta=es_correcta, explicacion=explicacion, siguiente_pregunta=siguiente
    )


class RespuestasFin(BaseModel):
    respuestas: List[dict]  # [{pregunta_id, opcion_seleccionada_id}]


class RespuestasRequest(BaseModel):
    respuestas: List[dict] = []


@router.post("/{simulacro_id}/finalizar")
async def finalizar_simulacro(
    simulacro_id: int,
    body: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Recibe respuestas y calcula resultado."""
    try:
        respuestas = body.get('respuestas', [])
        user_id = current_user["id"]
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Limpiar resultados anteriores
        cur.execute("DELETE FROM resultados_detalle WHERE simulacro_id = %s", (simulacro_id,))
        
        # Obtener preguntas del simulacro
        cur.execute("""
            SELECT rs.pregunta_id, rs.puntaje_pregunta 
            FROM respuestas_simulacro rs 
            WHERE rs.simulacro_id = %s ORDER BY rs.orden
        """, (simulacro_id,))
        preguntas = cur.fetchall()
        
        aciertos = 0
        errores = 0
        sin_responder = 0
        puntaje_total = 0.0
        
        # Procesar cada pregunta
        for pregunta_id, puntaje in preguntas:
            # Convertir puntaje a float
            puntaje_float = float(puntaje) if puntaje else 0.0
            
            # Buscar respuesta del usuario
            opcion_seleccionada_id = None
            for r in respuestas:
                if str(r.get('pregunta_id')) == str(pregunta_id):
                    opcion_seleccionada_id = r.get('opcion_seleccionada_id')
                    break
            
            # Obtener opción correcta
            cur.execute("SELECT id FROM opciones WHERE pregunta_id = %s AND es_correcta = TRUE", (pregunta_id,))
            opcion_correcta = cur.fetchone()
            
            es_correcta = False
            if opcion_seleccionada_id is None:
                sin_responder += 1
                es_correcta = False
            elif opcion_correcta and opcion_seleccionada_id == opcion_correcta[0]:
                aciertos += 1
                puntaje_total += puntaje_float
                es_correcta = True
            else:
                errores += 1
                puntaje_total -= 1.125
                es_correcta = False
            
            # Guardar detalle
            cur.execute("""
                INSERT INTO resultados_detalle (simulacro_id, pregunta_id, opcion_seleccionada_id, es_correcta)
                VALUES (%s, %s, %s, %s)
            """, (simulacro_id, pregunta_id, opcion_seleccionada_id, es_correcta))
        
        # Asegurar puntaje no negativo
        if puntaje_total < 0:
            puntaje_total = 0.0
        
        # Actualizar simulacro
        cur.execute("""
            UPDATE simulacros SET puntaje_total = %s, estado = 'finalizado' 
            WHERE id = %s
        """, (float(puntaje_total), simulacro_id))
        
        # Actualizar max/min puntaje del usuario
        cur.execute("""
            UPDATE usuarios SET 
                max_puntaje = GREATEST(COALESCE(max_puntaje, 0), %s),
                min_puntaje = LEAST(COALESCE(min_puntaje, 999999), %s)
            WHERE id = %s
        """, (float(puntaje_total), float(puntaje_total), user_id))
        
        conn.commit()

        # Crear flashcards de las preguntas falladas
        for pregunta_id, puntaje in preguntas:
            es_fallo = True
            for r in respuestas:
                if str(r.get('pregunta_id')) == str(pregunta_id):
                    opcion_seleccionada_id = r.get('opcion_seleccionada_id')
                    cur.execute("SELECT id FROM opciones WHERE pregunta_id = %s AND es_correcta = TRUE", (pregunta_id,))
                    opcion_correcta = cur.fetchone()
                    if opcion_correcta and opcion_seleccionada_id == opcion_correcta[0]:
                        es_fallo = False
                    break
            
            if es_fallo:
                cur.execute("""
                    INSERT INTO flashcards (usuario_id, pregunta_id, facilidad, intervalo, repeticiones, proxima_revision)
                    VALUES (%s, %s, 2500, 1, 0, CURRENT_DATE)
                    ON CONFLICT (usuario_id, pregunta_id) DO UPDATE
                    SET facilidad = 2500, intervalo = 1, repeticiones = 0, 
                        proxima_revision = CURRENT_DATE, estado = 'activa'
                """, (user_id, pregunta_id))

        conn.commit()
        conn.close()
        
        return {
            "id": simulacro_id,
            "puntaje_total": float(puntaje_total),
            "total_preguntas": len(preguntas),
            "aciertos": aciertos,
            "errores": errores,
            "sin_responder": sin_responder,
        }
    except Exception as e:
        import sys
        print("ERROR finalizar_simulacro: " + str(e), file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historial")
async def get_historial(current_user: dict = Depends(get_current_user)):
    """Obtiene historial de simulacros."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, fecha_inicio, puntaje_total, total_preguntas, estado
        FROM simulacros
        WHERE usuario_id = %s
        ORDER BY fecha_inicio DESC
        LIMIT 20
    """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {"id": r[0], "fecha": r[1], "puntaje": r[2], "total": r[3], "estado": r[4]}
        for r in rows
    ]


@router.get("/{simulacro_id}/resultado")
async def get_resultado(simulacro_id: int, current_user: dict = Depends(get_current_user)):
    """Obtiene resultado de un simulacro finalizado."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Obtiene resultado desde la tabla detalle (más rápido)
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN es_correcta THEN 1 ELSE 0 END) as aciertos,
            SUM(CASE WHEN NOT es_correcta AND opcion_seleccionada_id IS NOT NULL THEN 1 ELSE 0 END) as errores,
            SUM(CASE WHEN opcion_seleccionada_id IS NULL THEN 1 ELSE 0 END) as sin_responder,
            COALESCE(SUM(puntaje_obtenido), 0) as puntaje_total
        FROM resultados_detalle
        WHERE simulacro_id = %s
    """, (simulacro_id,))
    
    resultado = cur.fetchone()
    
    if not resultado or resultado[0] == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Resultado no encontrado")

    return {
        "id": simulacro_id,
        "total_preguntas": resultado[0],
        "aciertos": resultado[1] or 0,
        "errores": resultado[2] or 0,
        "sin_responder": resultado[3] or 0,
        "puntaje_total": max(0, float(resultado[4])),
    }
