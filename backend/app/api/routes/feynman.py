from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import connect
from typing import List
import sys

sys.path.insert(0, "C:/Users/Brian/Desktop/akademus/backend")

from app.core.config import get_settings
from app.core.security import get_current_user, require_role
from app.schemas import FeynmanExplicacion, FeynmanResponse, FeynmanCalificar


settings = get_settings()
router = APIRouter(prefix="/feynman", tags=["Feynman"])


def get_db_connection():
    return connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )


@router.get("/temas")
async def get_temas(current_user: dict = Depends(get_current_user)):
    """Lista temas disponibles para Feynman."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, curso_id FROM temas ORDER BY nombre")
    rows = cur.fetchall()
    conn.close()

    return [{"id": r[0], "nombre": r[1], "curso_id": r[2]} for r in rows]


@router.post("/explicacion", response_model=FeynmanResponse)
async def enviar_explicacion(
    data: FeynmanExplicacion, current_user: dict = Depends(get_current_user)
):
    """Envía explicación Feynman."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO revisiones_feynman (usuario_id, tema_id, explicacion_usuario)
        VALUES (%s, %s, %s)
        RETURNING id, tema_id, explicacion_usuario, puntaje_admin, comentario_admin, estado, fecha_creacion, fecha_revision
    """,
        (user_id, data.tema_id, data.explicacion),
    )

    row = cur.fetchone()
    conn.commit()
    conn.close()

    return FeynmanResponse(
        id=row[0],
        tema_id=row[1],
        explicacion_usuario=row[2],
        puntaje_admin=row[3],
        comentario_admin=row[4],
        estado=row[5],
        fecha_creacion=row[6],
        fecha_revision=row[7],
    )


@router.get("/mis-explicaciones", response_model=List[FeynmanResponse])
async def get_mis_explicaciones(current_user: dict = Depends(get_current_user)):
    """Historial de mis explicaciones."""
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, tema_id, explicacion_usuario, puntaje_admin, comentario_admin, estado, fecha_creacion, fecha_revision
        FROM revisiones_feynman
        WHERE usuario_id = %s
        ORDER BY fecha_creacion DESC
        LIMIT 20
    """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()

    return [
        FeynmanResponse(
            id=r[0],
            tema_id=r[1],
            explicacion_usuario=r[2],
            puntaje_admin=r[3],
            comentario_admin=r[4],
            estado=r[5],
            fecha_creacion=r[6],
            fecha_revision=r[7],
        )
        for r in rows
    ]


# ================== ADMIN ROUTES ==================

admin_router = APIRouter(prefix="/admin/feynman", tags=["Admin Feynman"])


@admin_router.get("/pendientes", response_model=List[FeynmanResponse])
async def get_pendientes(current_user: dict = Depends(require_role([1, 2]))):
    """Lista explicaciones pendientes (admin)."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tema_id, explicacion_usuario, puntaje_admin, comentario_admin, estado, fecha_creacion, fecha_revision
        FROM revisiones_feynman
        WHERE estado = 'pendiente'
        ORDER BY fecha_creacion
    """)
    rows = cur.fetchall()
    conn.close()

    return [
        FeynmanResponse(
            id=r[0],
            tema_id=r[1],
            explicacion_usuario=r[2],
            puntaje_admin=r[3],
            comentario_admin=r[4],
            estado=r[5],
            fecha_creacion=r[6],
            fecha_revision=r[7],
        )
        for r in rows
    ]


@admin_router.put("/{feynman_id}/calificar", response_model=FeynmanResponse)
async def calificar(
    feynman_id: int,
    data: FeynmanCalificar,
    current_user: dict = Depends(require_role([1, 2])),
):
    """Califica explicación (admin)."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE revisiones_feynman
        SET puntaje_admin = %s, comentario_admin = %s, estado = %s, fecha_revision = %s
        WHERE id = %s
        RETURNING id, tema_id, explicacion_usuario, puntaje_admin, comentario_admin, estado, fecha_creacion, fecha_revision
    """,
        (data.puntaje, data.comentario, data.estado, datetime.utcnow(), feynman_id),
    )

    row = cur.fetchone()
    conn.commit()
    conn.close()

    return FeynmanResponse(
        id=row[0],
        tema_id=row[1],
        explicacion_usuario=row[2],
        puntaje_admin=row[3],
        comentario_admin=row[4],
        estado=row[5],
        fecha_creacion=row[6],
        fecha_revision=row[7],
    )
