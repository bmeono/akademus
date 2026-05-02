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

    cur.execute("SELECT id, nombre FROM cursos ORDER BY orden")
    cursos = [{"id": r[0], "nombre": r[1]} for r in cur.fetchall()]

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


@router.get("/creditos")
async def get_creditos_simulacro(current_user: dict = Depends(get_current_user)):
    """Obtiene los simulacros disponibles del usuario."""
    user_id = current_user["id"]
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT simulacros_disponibles FROM usuarios WHERE id = %s", (user_id,))
    row = cur.fetchone()
    conn.close()
    return {"simulacros_disponibles": row[0] if row and row[0] is not None else 0}


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

    # ✅ Si hay un simulacro en curso para LA MISMA especialidad, devolver ese
    cur.execute(
        "SELECT id, total_preguntas, duracion_segundos, especialidad_id FROM simulacros WHERE usuario_id = %s AND estado = 'en_curso'",
        (user_id,)
    )
    en_curso = cur.fetchone()
    if en_curso:
        if en_curso[3] == config.especialidad_id:
            # Misma especialidad → continuar simulacro existente
            conn.close()
            return SimulacroStartResponse(
                simulacro_id=en_curso[0],
                total_preguntas=en_curso[1],
                duracion_segundos=en_curso[2],
            )
        else:
            # Diferente especialidad → finalizar el anterior sin descontar crédito
            cur.execute(
                "UPDATE simulacros SET estado = 'finalizado', puntaje_total = 0 WHERE id = %s",
                (en_curso[0],)
            )
            conn.commit()
            # Continúa para crear el nuevo simulacro

    # Verificar créditos disponibles
    cur.execute("SELECT simulacros_disponibles FROM usuarios WHERE id = %s", (user_id,))
    row = cur.fetchone()
    if not row or (row[0] is not None and row[0] <= 0):
        conn.close()
        raise HTTPException(status_code=403, detail="Sin simulacros disponibles. Contacta al administrador.")

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

    # Crear simulacro (180 minutos)
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

    fecha_inicio = simulacro[2]
    if fecha_inicio:
        import datetime
        ahora = datetime.datetime.now()
        elapsed = (ahora - fecha_inicio).total_seconds()
        tiempo_restante = max(0, duracion_segundos - elapsed)
    else:
        tiempo_restante = duracion_segundos

    cur.execute("""
        SELECT p.id, p.enunciado, p.explicacion, p.imagen_url, p.dificultad, r.orden, r.puntaje_pregunta, p.universidad, p.an_exam
        FROM preguntas p
        JOIN respuestas_simulacro r ON r.pregunta_id = p.id
        WHERE r.simulacro_id = %s
        ORDER BY r.orden
    """, (simulacro_id,))
    preguntas_raw = cur.fetchall()

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
        "total_preguntas": len(preguntas),
        "estado": simulacro[4]   # 'en_curso' | 'finalizado'
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

    tiempo_transcurrido = (datetime.utcnow() - simulacro[2]).total_seconds()
    if tiempo_transcurrido > simulacro[3]:
        cur.execute(
            "UPDATE simulacros SET estado = 'finalizado' WHERE id = %s", (simulacro_id,)
        )
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail="Tiempo agotado")

    cur.execute(
        "SELECT es_correcta FROM opciones WHERE id = %s", (data.opcion_seleccionada_id,)
    )
    opcion = cur.fetchone()

    if not opcion:
        conn.close()
        raise HTTPException(status_code=404, detail="Opción no encontrada")

    es_correcta = opcion[0]

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
                    enunciado=sig_pregunta[2],
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

    explicacion = None if es_correcta else data.get("explicacion")

    return RespuestaResultResponse(
        es_correcta=es_correcta, explicacion=explicacion, siguiente_pregunta=siguiente
    )


class RespuestasFin(BaseModel):
    respuestas: List[dict]


class RespuestasRequest(BaseModel):
    respuestas: List[dict] = []


@router.post("/{simulacro_id}/finalizar")
async def finalizar_simulacro(
    simulacro_id: int,
    body: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Recibe respuestas y calcula resultado. Versión optimizada."""
    try:
        respuestas_raw = body.get('respuestas', [])
        user_id = current_user["id"]

        # ── OPTIMIZACIÓN 1: convertir respuestas a dict O(1) en vez de loop O(n²)
        # { str(pregunta_id): opcion_seleccionada_id }
        respuestas_map = {
            str(r.get('pregunta_id')): r.get('opcion_seleccionada_id')
            for r in respuestas_raw
        }

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM resultados_detalle WHERE simulacro_id = %s", (simulacro_id,))

        # Obtener preguntas del simulacro
        cur.execute("""
            SELECT rs.pregunta_id, rs.puntaje_pregunta
            FROM respuestas_simulacro rs
            WHERE rs.simulacro_id = %s ORDER BY rs.orden
        """, (simulacro_id,))
        preguntas = cur.fetchall()

        pregunta_ids = [p[0] for p in preguntas]

        # ── OPTIMIZACIÓN 2: una sola query para todas las opciones correctas
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
        resultados_batch = []   # para insert masivo
        flashcards_batch = []   # para insert masivo

        for pregunta_id, puntaje in preguntas:
            puntaje_float = float(puntaje) if puntaje else 0.0

            # O(1) lookup con el dict
            opcion_seleccionada_id = respuestas_map.get(str(pregunta_id))
            opcion_correcta_id = opciones_correctas.get(pregunta_id)

            if opcion_seleccionada_id is None:
                sin_responder += 1
                # No respondida → no se guarda en resultados_detalle
                # Sí cuenta como fallo para flashcard
                flashcards_batch.append((user_id, pregunta_id))
            elif opcion_correcta_id and opcion_seleccionada_id == opcion_correcta_id:
                aciertos += 1
                puntaje_total += puntaje_float
                resultados_batch.append((simulacro_id, pregunta_id, opcion_seleccionada_id, True))
            else:
                errores += 1
                puntaje_total -= 1.125
                resultados_batch.append((simulacro_id, pregunta_id, opcion_seleccionada_id, False))
                flashcards_batch.append((user_id, pregunta_id))

        puntaje_total = round(puntaje_total, 2)

        # ── OPTIMIZACIÓN 3: insert masivo de resultados_detalle (1 query en vez de N)
        if resultados_batch:
            cur.executemany("""
                INSERT INTO resultados_detalle (simulacro_id, pregunta_id, opcion_seleccionada_id, es_correcta)
                VALUES (%s, %s, %s, %s)
            """, resultados_batch)

        # Actualizar simulacro
        cur.execute("""
            UPDATE simulacros SET puntaje_total = %s, estado = 'finalizado'
            WHERE id = %s
        """, (float(puntaje_total), simulacro_id))

        # ✅ Descontar crédito al finalizar (no al iniciar)
        cur.execute(
            "UPDATE usuarios SET simulacros_disponibles = GREATEST(0, simulacros_disponibles - 1) WHERE id = %s",
            (user_id,)
        )

        # Actualizar max/min puntaje del usuario
        cur.execute("""
            UPDATE usuarios SET
                max_puntaje = GREATEST(COALESCE(max_puntaje, 0), %s),
                min_puntaje = LEAST(COALESCE(min_puntaje, 999999), %s)
            WHERE id = %s
        """, (float(puntaje_total), float(puntaje_total), user_id))

        # ── OPTIMIZACIÓN 4: insert masivo de flashcards (1 query en vez de N)
        if flashcards_batch:
            cur.executemany("""
                INSERT INTO flashcards (usuario_id, pregunta_id, facilidad, intervalo, repeticiones, proxima_revision)
                VALUES (%s, %s, 2500, 1, 0, CURRENT_DATE)
                ON CONFLICT (usuario_id, pregunta_id) DO UPDATE
                SET facilidad = 2500, intervalo = 1, repeticiones = 0,
                    proxima_revision = CURRENT_DATE, estado = 'activa'
            """, flashcards_batch)

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

    cur.execute("""
        SELECT COALESCE(puntaje_total, 0), total_preguntas
        FROM simulacros
        WHERE id = %s AND estado = 'finalizado'
    """, (simulacro_id,))
    resultado = cur.fetchone()

    if not resultado:
        conn.close()
        raise HTTPException(status_code=404, detail="Resultado no encontrado")

    total_preguntas = resultado[1] or 0

    # Blancos = total - aciertos - errores (no se insertan en resultados_detalle)
    cur.execute("""
        SELECT
            SUM(CASE WHEN es_correcta THEN 1 ELSE 0 END),
            SUM(CASE WHEN NOT es_correcta THEN 1 ELSE 0 END)
        FROM resultados_detalle
        WHERE simulacro_id = %s
    """, (simulacro_id,))
    stats = cur.fetchone()
    conn.close()

    aciertos = int(stats[0] or 0)
    errores = int(stats[1] or 0)
    sin_responder = max(0, total_preguntas - aciertos - errores)

    return {
        "id": simulacro_id,
        "total_preguntas": total_preguntas,
        "aciertos": aciertos,
        "errores": errores,
        "sin_responder": sin_responder,
        "puntaje_total": max(0, float(resultado[0])),
    }


@router.get("/{simulacro_id}/resultado-pdf")
async def download_resultado_pdf(simulacro_id: int, token: str = None):
    """Genera PDF mejorado con resultados del simulacro."""
    from app.core.security import decode_token

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
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.pdfgen import canvas as pdfcanvas
    from io import BytesIO
    import datetime as dt

    # ── Colores corporativos
    AZUL_DARK  = colors.HexColor("#1e3a5f")
    AZUL_MED   = colors.HexColor("#2563eb")
    AZUL_LIGHT = colors.HexColor("#dbeafe")
    VERDE      = colors.HexColor("#16a34a")
    ROJO       = colors.HexColor("#dc2626")
    GRIS       = colors.HexColor("#f1f5f9")
    GRIS_TEXT  = colors.HexColor("#64748b")
    BLANCO     = colors.white

    conn = get_db_connection()
    cur  = conn.cursor()

    cur.execute("SELECT nombre_completo FROM usuarios WHERE id = %s", (user_id,))
    user_row = cur.fetchone()
    nombre_usuario = user_row[0] if user_row and user_row[0] else "Usuario"

    cur.execute("""
        SELECT s.especialidad_id, e.nombre, s.puntaje_total, s.fecha_inicio, s.total_preguntas
        FROM simulacros s LEFT JOIN especialidades e ON s.especialidad_id = e.id
        WHERE s.id = %s AND s.usuario_id = %s
    """, (simulacro_id, user_id))
    sim_row = cur.fetchone()
    if not sim_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Simulacro no encontrado")

    especialidad     = sim_row[1] or "General"
    puntaje_global   = float(sim_row[2] or 0)
    fecha_simulacro  = sim_row[3]
    total_preguntas  = sim_row[4] or 0

    cur.execute("SELECT grupo_academico_id FROM especialidades WHERE id = %s", (sim_row[0],))
    grupo_row = cur.fetchone()
    grupo_id  = grupo_row[0] if grupo_row else None

    cur.execute("""
        SELECT a.id, a.nombre, cp.numero_preguntas, cp.puntaje_pregunta
        FROM configuraciones_puntaje cp
        JOIN asignaturas a ON cp.asignatura_id = a.id
        WHERE cp.grupo_academico_id = %s AND cp.activo = TRUE
        ORDER BY a.orden, a.nombre
    """, (grupo_id,))
    configs = cur.fetchall()

    cur.execute("""
        SELECT p.asignatura_id,
               SUM(CASE WHEN rd.es_correcta THEN 1 ELSE 0 END),
               SUM(CASE WHEN NOT rd.es_correcta THEN 1 ELSE 0 END)
        FROM resultados_detalle rd
        JOIN preguntas p ON rd.pregunta_id = p.id
        WHERE rd.simulacro_id = %s
        GROUP BY p.asignatura_id
    """, (simulacro_id,))
    res_map = {r[0]: {'aciertos': int(r[1] or 0), 'errores': int(r[2] or 0)} for r in cur.fetchall()}
    conn.close()

    # ── Construir filas
    filas = []
    tot_preg = tot_ac = tot_err = tot_bl = tot_pts = 0
    for cfg in configs:
        asig_id, nombre, num_preg, pts_preg = cfg[0], cfg[1], cfg[2], float(cfg[3] or 1)
        res      = res_map.get(asig_id, {'aciertos': 0, 'errores': 0})
        ac       = res['aciertos']
        err      = res['errores']
        bl       = max(0, num_preg - ac - err)
        pts      = round(ac * pts_preg - err * 1.125, 2)
        filas.append({'asignatura': nombre, 'total': num_preg,
                      'aciertos': ac, 'errores': err, 'blancos': bl, 'puntaje': pts})
        tot_preg += num_preg; tot_ac += ac; tot_err += err
        tot_bl   += bl;       tot_pts += pts

    tot_pts = round(tot_pts, 2)

    # ── PDF con canvas de fondo + platypus encima
    buffer = BytesIO()
    page_w, page_h = A4

    # Canvas para fondo decorativo
    c = pdfcanvas.Canvas(buffer, pagesize=A4)

    # Franja superior azul oscuro
    c.setFillColor(AZUL_DARK)
    c.rect(0, page_h - 3.5*cm, page_w, 3.5*cm, fill=1, stroke=0)

    # Franja inferior fina
    c.setFillColor(AZUL_MED)
    c.rect(0, 0, page_w, 0.8*cm, fill=1, stroke=0)

    # Marca de agua diagonal
    c.saveState()
    c.setFillColor(colors.HexColor("#e2e8f0"))
    c.setFont("Helvetica-Bold", 72)
    c.translate(page_w / 2, page_h / 2)
    c.rotate(35)
    c.drawCentredString(0, 0, "AKADEMUS")
    c.restoreState()

    # Título en franja superior
    c.setFillColor(BLANCO)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(page_w / 2, page_h - 1.5*cm, "AKADEMUS")
    c.setFont("Helvetica", 11)
    c.drawCentredString(page_w / 2, page_h - 2.3*cm, "Resultado de Simulacro de Examen de Admisión")

    c.save()

    # ── Platypus encima del canvas de fondo
    buffer.seek(0)

    # Necesitamos un nuevo buffer limpio para platypus
    buf2 = BytesIO()

    styles = getSampleStyleSheet()

    def make_style(name, **kwargs):
        return ParagraphStyle(name, parent=styles['Normal'], **kwargs)

    doc = SimpleDocTemplate(
        buf2, pagesize=A4,
        topMargin=4.2*cm, bottomMargin=1.5*cm,
        leftMargin=1.5*cm, rightMargin=1.5*cm
    )

    elems = []

    # ── Bloque de datos del estudiante
    fecha_str = fecha_simulacro.strftime("%d/%m/%Y %H:%M") if fecha_simulacro else "—"
    info_data = [
        ["Estudiante:", nombre_usuario, "Fecha:", fecha_str],
        ["Especialidad:", especialidad, "Simulacro N°:", str(simulacro_id)],
    ]
    info_table = Table(info_data, colWidths=[3*cm, 7.5*cm, 3*cm, 4.5*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE',  (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), AZUL_DARK),
        ('TEXTCOLOR', (2,0), (2,-1), AZUL_DARK),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,0), (-1,-1), GRIS),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    elems.append(info_table)
    elems.append(Spacer(1, 0.5*cm))

    # ── Tarjetas de resumen (Aciertos / Errores / Blancos / Puntaje)
    resumen_data = [[
        Paragraph(f'<font size="20" color="#16a34a"><b>{tot_ac}</b></font><br/><font size="8" color="#64748b">ACIERTOS</font>', styles['Normal']),
        Paragraph(f'<font size="20" color="#dc2626"><b>{tot_err}</b></font><br/><font size="8" color="#64748b">ERRORES</font>', styles['Normal']),
        Paragraph(f'<font size="20" color="#64748b"><b>{tot_bl}</b></font><br/><font size="8" color="#64748b">BLANCOS</font>', styles['Normal']),
        Paragraph(f'<font size="20" color="#2563eb"><b>{tot_pts:.2f}</b></font><br/><font size="8" color="#64748b">PUNTAJE</font>', styles['Normal']),
    ]]
    resumen_table = Table(resumen_data, colWidths=[4.4*cm]*4)
    resumen_table.setStyle(TableStyle([
        ('ALIGN',    (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',   (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f0fdf4")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#fef2f2")),
        ('BACKGROUND', (2,0), (2,0), GRIS),
        ('BACKGROUND', (3,0), (3,0), AZUL_LIGHT),
        ('BOX',      (0,0), (0,0), 0.5, colors.HexColor("#86efac")),
        ('BOX',      (1,0), (1,0), 0.5, colors.HexColor("#fca5a5")),
        ('BOX',      (2,0), (2,0), 0.5, colors.HexColor("#cbd5e1")),
        ('BOX',      (3,0), (3,0), 0.5, colors.HexColor("#93c5fd")),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
    ]))
    elems.append(resumen_table)
    elems.append(Spacer(1, 0.5*cm))

    # ── Título de tabla
    elems.append(Paragraph(
        '<font color="#1e3a5f"><b>DETALLE POR ASIGNATURA</b></font>',
        make_style('SecTitle', fontSize=10, spaceAfter=6)
    ))
    elems.append(HRFlowable(width="100%", thickness=1.5, color=AZUL_MED, spaceAfter=4))

    # ── Tabla detalle
    header = [
        Paragraph('<b>N°</b>',         make_style('H', fontSize=8, textColor=BLANCO, alignment=1)),
        Paragraph('<b>Asignatura</b>',  make_style('H', fontSize=8, textColor=BLANCO)),
        Paragraph('<b>Total</b>',       make_style('H', fontSize=8, textColor=BLANCO, alignment=1)),
        Paragraph('<b>Aciertos</b>',    make_style('H', fontSize=8, textColor=BLANCO, alignment=1)),
        Paragraph('<b>Errores</b>',     make_style('H', fontSize=8, textColor=BLANCO, alignment=1)),
        Paragraph('<b>Blancos</b>',     make_style('H', fontSize=8, textColor=BLANCO, alignment=1)),
        Paragraph('<b>Puntaje</b>',     make_style('H', fontSize=8, textColor=BLANCO, alignment=1)),
    ]
    table_data = [header]

    for idx, row in enumerate(filas, 1):
        bg = BLANCO if idx % 2 == 0 else GRIS
        pts_color = "#16a34a" if row['puntaje'] > 0 else "#dc2626"
        table_data.append([
            Paragraph(str(idx), make_style(f'C{idx}', fontSize=8, alignment=1)),
            Paragraph(row['asignatura'], make_style(f'A{idx}', fontSize=8)),
            Paragraph(str(row['total']),    make_style(f'T{idx}', fontSize=8, alignment=1)),
            Paragraph(f'<font color="#16a34a"><b>{row["aciertos"]}</b></font>',
                      make_style(f'Ac{idx}', fontSize=8, alignment=1)),
            Paragraph(f'<font color="#dc2626"><b>{row["errores"]}</b></font>',
                      make_style(f'Er{idx}', fontSize=8, alignment=1)),
            Paragraph(str(row['blancos']),  make_style(f'Bl{idx}', fontSize=8, alignment=1)),
            Paragraph(f'<font color="{pts_color}"><b>{row["puntaje"]:.2f}</b></font>',
                      make_style(f'Pt{idx}', fontSize=8, alignment=1)),
        ])

    # Fila total
    table_data.append([
        Paragraph('', make_style('T0', fontSize=8)),
        Paragraph('<b>TOTAL</b>', make_style('TT', fontSize=9, textColor=AZUL_DARK)),
        Paragraph(f'<b>{tot_preg}</b>', make_style('TP', fontSize=9, alignment=1)),
        Paragraph(f'<b><font color="#16a34a">{tot_ac}</font></b>',  make_style('TAc', fontSize=9, alignment=1)),
        Paragraph(f'<b><font color="#dc2626">{tot_err}</font></b>', make_style('TEr', fontSize=9, alignment=1)),
        Paragraph(f'<b>{tot_bl}</b>',  make_style('TBl', fontSize=9, alignment=1)),
        Paragraph(f'<b>{tot_pts:.2f}</b>', make_style('TPt', fontSize=9, alignment=1, textColor=AZUL_MED)),
    ])

    n = len(table_data)
    col_w = [0.7*cm, 6.5*cm, 1.2*cm, 1.5*cm, 1.3*cm, 1.3*cm, 1.7*cm]
    det_table = Table(table_data, colWidths=col_w, repeatRows=1)

    row_styles = [
        ('BACKGROUND',    (0,0), (-1,0), AZUL_DARK),
        ('ROWBACKGROUNDS',(0,1), (-1,n-2), [BLANCO, GRIS]),
        ('BACKGROUND',    (0,n-1), (-1,n-1), AZUL_LIGHT),
        ('FONTNAME',      (0,n-1), (-1,n-1), 'Helvetica-Bold'),
        ('GRID',          (0,0), (-1,-1), 0.3, colors.HexColor("#cbd5e1")),
        ('LINEBELOW',     (0,0), (-1,0), 1, AZUL_MED),
        ('LINEABOVE',     (0,n-1), (-1,n-1), 1, AZUL_MED),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('ALIGN',         (1,0), (1,-1), 'LEFT'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (1,0), (1,-1), 4),
    ]
    det_table.setStyle(TableStyle(row_styles))
    elems.append(det_table)
    elems.append(Spacer(1, 0.4*cm))

    # ── Penalización nota al pie
    elems.append(Paragraph(
        '<font size="7" color="#64748b">* Penalización por respuesta incorrecta: -1.125 pts &nbsp;|&nbsp; Sin responder: 0 pts</font>',
        make_style('Foot', fontSize=7, textColor=GRIS_TEXT)
    ))

    # ── Construir PDF platypus con fondo canvas
    class BackgroundCanvas:
        def __init__(self, bg_func):
            self.bg_func = bg_func
        def __call__(self, canvas_obj, doc):
            self.bg_func(canvas_obj, doc)

    def draw_background(c, doc):
        c.saveState()
        # Franja superior
        c.setFillColor(AZUL_DARK)
        c.rect(0, page_h - 3.5*cm, page_w, 3.5*cm, fill=1, stroke=0)
        # Franja inferior
        c.setFillColor(AZUL_MED)
        c.rect(0, 0, page_w, 0.8*cm, fill=1, stroke=0)
        # Marca de agua
        c.setFillColor(colors.HexColor("#e2e8f0"))
        c.setFont("Helvetica-Bold", 80)
        c.translate(page_w/2, page_h/2)
        c.rotate(35)
        c.drawCentredString(0, 0, "AKADEMUS")
        c.restoreState()
        # Título
        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(page_w/2, page_h - 1.4*cm, "AKADEMUS")
        c.setFont("Helvetica", 10)
        c.drawCentredString(page_w/2, page_h - 2.2*cm, "Resultado de Simulacro de Examen de Admisión")
        # Número de página
        c.setFillColor(BLANCO)
        c.setFont("Helvetica", 8)
        c.drawCentredString(page_w/2, 0.25*cm, f"Generado el {dt.datetime.now().strftime('%d/%m/%Y %H:%M')}")

    doc.build(elems, onFirstPage=draw_background, onLaterPages=draw_background)

    buf2.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        buf2,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=resultado_simulacro_{simulacro_id}.pdf"}
    )
