from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2 import connect
from typing import List
import sys

sys.path.insert(0, "C:/Users/Brian/Desktop/akademus/backend")

from app.core.config import get_settings
from app.core.security import get_current_user
from app.schemas import (
    UserResponse,
    UserUpdate,
    EspecialidadResponse,
    GrupoEspecialidadResponse,
    ErrorResponse,
)


settings = get_settings()
router = APIRouter(prefix="/users", tags=["Usuarios"])


def get_db_connection():
    return connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Obtiene datos del usuario actual."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, nombre_completo, email, telefono, rol_id, especialidad_id, 
               two_factor_enabled, fecha_registro, ultimo_login
        FROM usuarios WHERE id = %s
    """,
        (user_id,),
    )
    user = cur.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return UserResponse(
        id=user[0],
        nombre_completo=user[1],
        email=user[2],
        telefono=user[3] or "",
        rol_id=user[4],
        especialidad_id=user[5],
        two_factor_enabled=user[6],
        fecha_registro=user[7],
        ultimo_login=user[8],
    )


@router.put("/me", response_model=UserResponse)
async def update_me(data: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Actualiza datos del usuario actual."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    update_fields = []
    values = []

    if data.nombre_completo:
        update_fields.append("nombre_completo = %s")
        values.append(data.nombre_completo)
    if data.telefono:
        update_fields.append("telefono = %s")
        values.append(data.telefono)
    if data.especialidad_id:
        update_fields.append("especialidad_id = %s")
        values.append(data.especialidad_id)

    if not update_fields:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    values.append(user_id)
    query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id = %s RETURNING id, nombre_completo, email, telefono, rol_id, especialidad_id, two_factor_enabled, fecha_registro, ultimo_login"

    cur.execute(query, values)
    user = cur.fetchone()
    conn.commit()
    conn.close()

    return UserResponse(
        id=user[0],
        nombre_completo=user[1],
        email=user[2],
        telefono=user[3] or "",
        rol_id=user[4],
        especialidad_id=user[5],
        two_factor_enabled=user[6],
        fecha_registro=user[7],
        ultimo_login=user[8],
    )


@router.get("/especialidades", response_model=List[EspecialidadResponse])
async def get_especialidades():
    """Lista todas las especialidades."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre, grupo_id, puntaje_minimo FROM especialidades ORDER BY grupo_id, orden"
    )
    rows = cur.fetchall()
    conn.close()

    return [
        EspecialidadResponse(id=r[0], nombre=r[1], grupo_id=r[2], puntaje_minimo=r[3])
        for r in rows
    ]


@router.get("/especialidades/grupos", response_model=List[GrupoEspecialidadResponse])
async def get_grupos_especialidad():
    """Lista grupos de especialidad."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre, descripcion, orden FROM grupos_especialidad ORDER BY orden"
    )
    rows = cur.fetchone()

    return [
        GrupoEspecialidadResponse(id=r[0], nombre=r[1], descripcion=r[2], orden=r[3])
        for r in rows
    ]


# Endpoints para preguntas de usuarios
@router.post("/preguntas")
async def create_pregunta_usuario(
    asignatura_id: int,
    enunciado: str,
    opciones: List[dict],
    explicacion: str = None,
    dificultad: int = 3,
    current_user: dict = Depends(get_current_user)
):
    """Usuario crea una pregunta para validación"""
    user_id = current_user["id"]
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""INSERT INTO preguntas (asignatura_id, enunciado, explicacion, dificultad, activa, estado, usuario_id) 
                VALUES (%s, %s, %s, %s, TRUE, 'pendiente', %s) RETURNING id""", 
                (asignatura_id, enunciado, explicacion, dificultad, user_id))
    pregunta_id = cur.fetchone()[0]
    
    for opt in opciones:
        cur.execute("""INSERT INTO opciones (pregunta_id, texto, es_correcta, activa) 
                    VALUES (%s, %s, %s, TRUE)""", 
                    (pregunta_id, opt.get('texto'), opt.get('es_correcta', False)))
    
    conn.commit()
    conn.close()
    return {"id": pregunta_id, "message": "Pregunta enviada para validación"}


@router.get("/mis-preguntas")
async def get_mis_preguntas(current_user: dict = Depends(get_current_user)):
    """Usuario ve sus preguntas creadas"""
    user_id = current_user["id"]
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""SELECT p.id, p.asignatura_id, p.enunciado, p.explicacion, p.dificultad, p.estado, p.motivo_rechazo, a.nombre
                FROM preguntas p
                LEFT JOIN asignaturas a ON p.asignatura_id = a.id
                WHERE p.usuario_id = %s
                ORDER BY p.id DESC""", (user_id,))
    rows = cur.fetchall()
    
    result = []
    for r in rows:
        cur.execute("SELECT id, texto, es_correcta FROM opciones WHERE pregunta_id = %s", (r[0],))
        opts = [{"id": o[0], "texto": o[1], "es_correcta": o[2]} for o in cur.fetchall()]
        result.append({
            "id": r[0], "asignatura_id": r[1], "enunciado": r[2], "explicacion": r[3],
            "dificultad": r[4], "estado": r[5], "motivo_rechazo": r[6], "asignatura_nombre": r[7], "opciones": opts
        })
    
    conn.close()
    return result


@router.post("/preguntas/{pregunta_id}/reportar")
async def reportar_pregunta(pregunta_id: int, motivo: str, current_user: dict = Depends(get_current_user)):
    """Usuario reporta una pregunta"""
    user_id = current_user["id"]
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT estado FROM preguntas WHERE id = %s", (pregunta_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    if row[0] == "aprobado":
        conn.close()
        raise HTTPException(status_code=400, detail="No puedes reportar preguntas validadas")
    
    cur.execute("""INSERT INTO reportes_preguntas (pregunta_id, usuario_id, motivo) VALUES (%s, %s, %s)""", 
                (pregunta_id, user_id, motivo))
    conn.commit()
    conn.close()
    return {"message": "Reporte enviado"}
