import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import List, Optional
from app.core.db import get_db_connection
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

router = APIRouter(prefix="/simulacros", tags=["Simulacros"])


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
        SELECT p.id, p.tema_id, p.enunciado, p.explicacion, p.imagen_url, p.dificultad, p.universidad, p.an_exam
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
            universidad=pregunta[6] if len(pregunta) > 6 else None,
            an_exam=pregunta[7] if len(pregunta) > 7 else None,
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
        SELECT p.id, p.enunciado, p.explicacion, p.imagen_url, p.dificultad, r.orden, r.puntaje_pregunta, p.universidad, p.an_exam
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
            "universidad": p[7] if len(p) > 7 else None,
            "an_exam": p[8] if len(p) > 8 else None,
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
            SELECT p.id, p.tema_id, p.enunciado, p.explicacion, p.imagen_url, p.dificultad, p.universidad, p.an_exam
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
                    enunciado=sig_preunta[2],
                    explicacion=sig_pregunta[3],
                    imagen_url=sig_pregunta[4],
                    dificultad=sig_pregunta[5],
                    universidad=sig_pregunta[6] if len(sig_pregunta) > 6 else None,
                    an_exam=sig_pregunta[7] if len(sig_pregunta) > 7 else None,
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
        
        # Fetch all correct options at once (optimization)
        pregunta_ids = [p[0] for p in preguntas]
        opciones_correctas = {}
        if pregunta_ids:
            cur.execute("""
                SELECT pregunta_id, id FROM opciones 
                WHERE pregunta_id IN %s AND es_correcta = TRUE
            """, (tuple(pregunta_ids),))
            for p_id, opt_id in cur.fetchall():
                opciones_correctas[p_id] = opt_id
        
        aciertos = 0
        errores = 0
        sin_responder = 0
        puntaje_total = 0.0
        
        # Procesar cada pregunta
        for pregunta_id, puntaje in preguntas:
            puntaje_float = float(puntaje) if puntaje else 0.0
            
            opcion_seleccionada_id = None
            for r in respuestas:
                if str(r.get('pregunta_id')) == str(pregunta_id):
                    opcion_seleccionada_id = r.get('opcion_seleccionada_id')
                    break
            
            opcion_correcta_id = opciones_correctas.get(pregunta_id)
            
            es_correcta = None  # None = no respondida, True = correcta, False = incorrecta
            if opcion_seleccionada_id is None:
                sin_responder += 1
                es_correcta = None  # No respondida
            elif opcion_correcta_id and opcion_seleccionada_id == opcion_correcta_id:
                aciertos += 1
                puntaje_total += puntaje_float
                es_correcta = True
            else:
                errores += 1
                puntaje_total -= 1.125
                es_correcta = False
            
            # Solo guardar si respondio (no guardar si no respondio)
            if es_correcta is not None:
                cur.execute("""
                    INSERT INTO resultados_detalle (simulacro_id, pregunta_id, opcion_seleccionada_id, es_correcta)
                    VALUES (%s, %s, %s, %s)
                """, (simulacro_id, pregunta_id, opcion_seleccionada_id, es_correcta))
        
        # Redondear a 2 decimales
        puntaje_total = round(puntaje_total, 2)
        
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

    # Obtiene resultado desde la tabla simulacros
    cur.execute("""
        SELECT 
            COALESCE(puntaje_total, 0) as puntaje_total,
            total_preguntas
        FROM simulacros
        WHERE id = %s AND estado = 'finalizado'
    """, (simulacro_id,))
    
    resultado = cur.fetchone()
    
    if not resultado:
        conn.close()
        raise HTTPException(status_code=404, detail="Resultado no encontrado")

    # Obtener stats desde resultados_detalle
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN es_correcta THEN 1 ELSE 0 END) as aciertos,
            SUM(CASE WHEN NOT es_correcta AND opcion_seleccionada_id IS NOT NULL THEN 1 ELSE 0 END) as errores,
            SUM(CASE WHEN opcion_seleccionada_id IS NULL THEN 1 ELSE 0 END) as sin_responder
        FROM resultados_detalle
        WHERE simulacro_id = %s
    """, (simulacro_id,))
    stats = cur.fetchone()
    
    return {
        "id": simulacro_id,
        "total_preguntas": stats[0] or 0,
        "aciertos": stats[1] or 0,
        "errores": stats[2] or 0,
        "sin_responder": stats[3] or 0,
        "puntaje_total": max(0, float(resultado[0])),
    }


@router.get("/{simulacro_id}/resultado-pdf")
async def download_resultado_pdf(simulacro_id: int, token: str = None):
    """
    Genera PDF con los resultados del simulacro.
    Acepta token como query parameter.
    """
    from fastapi.security import HTTPBearer
    from app.core.security import decode_token
    
    # Si viene token en query, usarlo
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")
    
    try:
        payload = decode_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token sin usuario")
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    
    # user_id viene del token ya decodificado arriba
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Obtener datos del usuario
    cur.execute("SELECT nombre_completo FROM usuarios WHERE id = %s", (user_id,))
    user_row = cur.fetchone()
    nombre_usuario = user_row[0] if user_row and user_row[0] else "Usuario"
    
    # Obtener datos del simulacro
    cur.execute("""
        SELECT s.especialidad_id, e.nombre, s.estado, s.puntaje_total, s.fecha_inicio
        FROM simulacros s
        LEFT JOIN especialidades e ON s.especialidad_id = e.id
        WHERE s.id = %s AND s.usuario_id = %s
    """, (simulacro_id, user_id))
    sim_row = cur.fetchone()
    if not sim_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Simulacro no encontrado")
    
    especialidad = sim_row[1] or "General"
    
    # Obtener el grupo académico de la especialidad
    cur.execute("""
        SELECT grupo_academico_id FROM especialidades WHERE id = %s
    """, (sim_row[0],))
    grupo_row = cur.fetchone()
    grupo_id = grupo_row[0] if grupo_row else None
    
    # Obtener TODAS las configuraciones de puntaje del grupo (para mostrar todas las asignaturas)
    cur.execute("""
        SELECT a.id, a.nombre, a.orden, cp.numero_preguntas, cp.puntaje_pregunta
        FROM configuraciones_puntaje cp
        JOIN asignaturas a ON cp.asignatura_id = a.id
        WHERE cp.grupo_academico_id = %s AND cp.activo = TRUE
        ORDER BY a.orden, a.nombre
    """, (grupo_id,))
    configs = cur.fetchall()
    
    # Obtener resultados del detalle (para calcular aciertos/errores/blancos)
    cur.execute("""
        SELECT 
            p.asignatura_id,
            COUNT(*) as total_respuestas,
            SUM(CASE WHEN rd.es_correcta THEN 1 ELSE 0 END) as aciertos,
            SUM(CASE WHEN NOT rd.es_correcta AND rd.opcion_seleccionada_id IS NOT NULL THEN 1 ELSE 0 END) as errores,
            SUM(CASE WHEN rd.opcion_seleccionada_id IS NULL THEN 1 ELSE 0 END) as blancos
        FROM resultados_detalle rd
        JOIN preguntas p ON rd.pregunta_id = p.id
        WHERE rd.simulacro_id = %s
        GROUP BY p.asignatura_id
    """, (simulacro_id,))
    resultados_raw = cur.fetchall()
    
    # Mapear resultados por asignatura_id
    resultados_map = {}
    for r in resultados_raw:
        resultados_map[r[0]] = {
            'aciertos': r[2] or 0,
            'errores': r[3] or 0,
            'blancos': r[4] or 0
        }
    
    # Construir lista de resultados por asignatura
    resultados_asignatura = []
    for cfg in configs:
        asignat_id = cfg[0]
        nombre = cfg[1]
        orden = cfg[2]
        num_preguntas = cfg[3]
        puntaje_pregunta = float(cfg[4]) if cfg[4] else 1.0
        
        res = resultados_map.get(asignat_id, {'aciertos': 0, 'errores': 0, 'blancos': 0})
        aciertos = res['aciertos']
        errores = res['errores']
        blancos = res['blancos']
        
        # Calcular puntaje: acierto * puntaje_pregunta - errores * 1.125 (penalidad)
        puntaje = (aciertos * puntaje_pregunta) - (errores * 1.125)
            
        resultados_asignatura.append({
            'asignatura': nombre,
            'total': num_preguntas,
            'aciertos': aciertos,
            'errores': errores,
            'blancos': blancos,
            'puntaje': round(puntaje, 2)
        })
    
    # Obtener total general desde la tabla simulacros
    cur.execute("""
        SELECT 
            COALESCE(puntaje_total, 0) as puntaje
        FROM simulacros
        WHERE id = %s
    """, (simulacro_id,))
    total_row = cur.fetchone()
    
    conn.close()
    
    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo para标题
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#1e40af"),
        spaceAfter=20,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=30,
        alignment=1
    )
    
    # Fondo con watermark (simulado con color de fondo)
    from reportlab.pdfgen import canvas
    pdf = canvas.Canvas(buffer)
    pdf.setFillColor(colors.HexColor("#f0f9ff"))
    pdf.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    
    # Logo Akademus (texto como marca de agua)
    pdf.setFillColor(colors.HexColor("#bfdbfe"))
    pdf.setFont("Helvetica-Bold", 60)
    pdf.saveState()
    pdf.translate(50, 300)
    pdf.rotate(45)
    pdf.drawCentredString(0, 0, "AKADEMUS")
    pdf.restoreState()
    
    # Continuar con elementos del documento
    elements.append(Paragraph("AKADEMUS", title_style))
    elements.append(Paragraph(f"SIMULACRO DE EXAMEN - {especialidad}", subtitle_style))
    elements.append(Paragraph(f"NOMBRE: {nombre_usuario}", ParagraphStyle('Nombre', parent=styles['Normal'], fontSize=12, spaceAfter=20)))
    
    # Tabla de resultados
    data = [["Nº", "Asignatura", "Total", "Aciertos", "Errores", "Blancos", "Puntaje"]]
    
    total_puntaje = 0
    total_total = 0
    total_aciertos = 0
    total_errores = 0
    total_blancos = 0
    
    for idx, row in enumerate(resultados_asignatura, 1):
        data.append([
            str(idx),
            row['asignatura'],
            str(row['total']),
            str(row['aciertos']),
            str(row['errores']),
            str(row['blancos']),
            f"{row['puntaje']:.2f}"
        ])
        total_total += row['total']
        total_aciertos += row['aciertos']
        total_errores += row['errores']
        total_blancos += row['blancos']
        total_puntaje += row['puntaje']
    
    # Fila de total
    data.append(["", "TOTAL", str(total_total), str(total_aciertos), str(total_errores), str(total_blancos), f"{round(total_puntaje, 2):.2f}"])
    
    tabla = Table(data, colWidths=[0.4*inch, 2*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 1*inch])
    
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e40af")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#e0f2fe")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    tabla.setStyle(estilo_tabla)
    elements.append(tabla)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"<b>TOTAL PUNTAJE OBTENIDO: {round(total_puntaje, 2):.2f}</b>", ParagraphStyle('Total', parent=styles['Normal'], fontSize=14, textColor=colors.HexColor("#1e40af"), alignment=2)))
    
    doc.build(elements)
    
    buffer.seek(0)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=resultado_simulacro_{simulacro_id}.pdf"}
    )
