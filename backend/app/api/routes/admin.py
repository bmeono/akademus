from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from psycopg2 import connect
from pydantic import BaseModel
import sys
sys.path.insert(0, "C:/Users/Brian/Desktop/akademus/backend")
from app.core.config import get_settings
from app.core.security import require_role

settings = get_settings()
router = APIRouter(prefix="/admin", tags=["Admin"])
http_bearer = HTTPBearer(auto_error=False)

def get_db_connection():
    return connect(host=settings.db_host, port=settings.db_port, user=settings.db_user, password=settings.db_password, database=settings.db_name)

class GrupoCreate(BaseModel): nombre: str; descripcion: str = None; orden: int = 0
class GrupoUpdate(BaseModel): nombre: str = None; descripcion: str = None; orden: int = None
class EspecialidadCreate(BaseModel): nombre: str; grupo_academico_id: int; codigo: str = None; puntaje_minimo: int = 0; orden: int = 0
class EspecialidadUpdate(BaseModel): nombre: str = None; grupo_academico_id: int = None; codigo: str = None; puntaje_minimo: int = None; orden: int = None
class CursoCreate(BaseModel): nombre: str; descripcion: str = None; orden: int = 0; imagen_url: str = None
class CursoUpdate(BaseModel): nombre: str = None; descripcion: str = None; orden: int = None; imagen_url: str = None; activo: bool = None
class TemaCreate(BaseModel): nombre: str; curso_id: int; dificultad_base: int = 3; imagen_url: str = None
class TemaUpdate(BaseModel): nombre: str = None; curso_id: int = None; dificultad_base: int = None; imagen_url: str = None; activo: bool = None
class PreguntaCreate(BaseModel): tema_id: int = None; asignatura_id: int = None; enunciado: str; explicacion: str = None; dificultad: int = 3; tipo_id: int = None; activa: bool = True; imagen_url: str = None; usuario_id: int = None
class PreguntaUpdate(BaseModel): tema_id: int = None; asignatura_id: int = None; enunciado: str = None; explicacion: str = None; dificultad: int = None; tipo_id: int = None; activa: bool = None; imagen_url: str = None; estado: str = None; motivo_rechazo: str = None
class OpcionCreate(BaseModel): texto: str; es_correcta: bool; activa: bool = True
class OpcionUpdate(BaseModel): texto: str = None; es_correcta: bool = None; activa: bool = None
class BloqueCreate(BaseModel): codigo: str; nombre: str; descripcion: str = None; orden: int = 0
class BloqueUpdate(BaseModel): codigo: str = None; nombre: str = None; descripcion: str = None; orden: int = None
class AreaCreate(BaseModel): bloque_id: int; codigo: str = None; nombre: str; descripcion: str = None; orden: int = 0
class AreaUpdate(BaseModel): bloque_id: int = None; codigo: str = None; nombre: str = None; descripcion: str = None; orden: int = None
class AsignaturaCreate(BaseModel): area_id: int; nombre: str; descripcion: str = None; orden: int = 0
class AsignaturaUpdate(BaseModel): area_id: int = None; nombre: str = None; descripcion: str = None; orden: int = None
class GrupoAcadCreate(BaseModel): codigo: str; nombre: str; descripcion: str = None; orden: int = 0
class GrupoAcadUpdate(BaseModel): codigo: str = None; nombre: str = None; descripcion: str = None; orden: int = None
class ConfigPuntajeCreate(BaseModel): grupo_academico_id: int; asignatura_id: int; numero_preguntas: int; puntaje_pregunta: float
class ConfigPuntajeUpdate(BaseModel): numero_preguntas: int = None; puntaje_pregunta: float = None

@router.get("/usuarios")
def get_usuarios(current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT id, email, rol_id, activo, fecha_registro FROM usuarios ORDER BY id")
    rows = cur.fetchall(); conn.close()
    return [{"id": str(r[0]), "email": r[1], "rol_id": r[2], "activo": r[3], "fecha_registro": str(r[4])} for r in rows]

@router.get("/grupos")
def get_grupos(current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT id, nombre, descripcion, orden FROM grupos_especialidad ORDER BY orden")
    rows = cur.fetchall(); conn.close()
    return [{"id": str(r[0]), "nombre": r[1], "descripcion": r[2], "orden": r[3]} for r in rows]

@router.post("/grupos")
def create_grupo(data: GrupoCreate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO grupos_especialidad (nombre, descripcion, orden) VALUES (%s, %s, %s) RETURNING id", (data.nombre, data.descripcion, data.orden))
    conn.commit(); conn.close()
    return {"nombre": data.nombre}

@router.put("/grupos/{grupo_id}")
def update_grupo(grupo_id: str, data: GrupoUpdate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    updates, values = [], []
    if data.nombre: updates.append("nombre = %s"); values.append(data.nombre)
    if data.descripcion is not None: updates.append("descripcion = %s"); values.append(data.descripcion)
    if data.orden is not None: updates.append("orden = %s"); values.append(data.orden)
    values.append(grupo_id)
    cur.execute(f"UPDATE grupos_especialidad SET {', '.join(updates)} WHERE id = %s", values)
    conn.commit(); conn.close()
    return {"id": grupo_id}

@router.delete("/grupos/{grupo_id}")
def delete_grupo(grupo_id: str, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM grupos_especialidad WHERE id = %s", (grupo_id,))
    conn.commit(); conn.close()
    return {"message": "Grupo eliminado"}

@router.get("/especialidades")
def get_especialidades(grupo_academico_id: int = None, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT e.id, e.nombre, e.grupo_academico_id, e.puntaje_minimo, e.orden, e.codigo, COALESCE(g.nombre, 'N/A') FROM especialidades e LEFT JOIN grupos_academicos g ON e.grupo_academico_id = g.id ORDER BY e.grupo_academico_id, e.codigo")
    rows = cur.fetchall(); conn.close()
    return [{"id": str(r[0]), "nombre": r[1], "grupo_academico_id": r[2], "puntaje_minimo": r[3], "orden": r[4], "codigo": r[5], "grupo_nombre": r[6]} for r in rows]

@router.post("/especialidades")
def create_especialidad(data: EspecialidadCreate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO especialidades (nombre, grupo_academico_id, codigo, puntaje_minimo, orden) VALUES (%s, %s, %s, %s, %s) RETURNING id", (data.nombre, data.grupo_academico_id, data.codigo, data.puntaje_minimo, data.orden))
    conn.commit(); conn.close()
    return {"nombre": data.nombre}

@router.put("/especialidades/{esp_id}")
def update_especialidad(esp_id: int, data: EspecialidadUpdate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    updates, values = [], []
    if data.nombre: updates.append("nombre = %s"); values.append(data.nombre)
    if data.grupo_academico_id: updates.append("grupo_academico_id = %s"); values.append(data.grupo_academico_id)
    if data.codigo: updates.append("codigo = %s"); values.append(data.codigo)
    if data.puntaje_minimo is not None: updates.append("puntaje_minimo = %s"); values.append(data.puntaje_minimo)
    if data.orden is not None: updates.append("orden = %s"); values.append(data.orden)
    values.append(esp_id)
    cur.execute(f"UPDATE especialidades SET {', '.join(updates)} WHERE id = %s", values); conn.commit(); conn.close()
    return {"id": esp_id}

@router.delete("/especialidades/{esp_id}")
def delete_especialidad(esp_id: str, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM especialidades WHERE id = %s", (esp_id,))
    conn.commit(); conn.close()
    return {"message": "Especialidad eliminada"}

@router.get("/cursos")
def get_cursos(current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT id, nombre, descripcion, orden, imagen_url, activo FROM cursos ORDER BY orden")
    rows = cur.fetchall(); conn.close()
    return [{"id": str(r[0]), "nombre": r[1], "descripcion": r[2], "orden": r[3], "imagen_url": r[4], "activo": r[5]} for r in rows]

@router.post("/cursos")
def create_curso(data: CursoCreate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO cursos (nombre, descripcion, orden, imagen_url) VALUES (%s, %s, %s, %s) RETURNING id", (data.nombre, data.descripcion, data.orden, data.imagen_url))
    conn.commit(); conn.close()
    return {"nombre": data.nombre}

@router.put("/cursos/{curso_id}")
def update_curso(curso_id: str, data: CursoUpdate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    updates, values = [], []
    if data.nombre: updates.append("nombre = %s"); values.append(data.nombre)
    if data.descripcion is not None: updates.append("descripcion = %s"); values.append(data.descripcion)
    if data.orden is not None: updates.append("orden = %s"); values.append(data.orden)
    if data.imagen_url is not None: updates.append("imagen_url = %s"); values.append(data.imagen_url)
    if data.activo is not None: updates.append("activo = %s"); values.append(data.activo)
    values.append(curso_id)
    cur.execute(f"UPDATE cursos SET {', '.join(updates)} WHERE id = %s", values)
    conn.commit(); conn.close()
    return {"id": curso_id}

@router.delete("/cursos/{curso_id}")
def delete_curso(curso_id: str, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM cursos WHERE id = %s", (curso_id,))
    conn.commit(); conn.close()
    return {"message": "Curso eliminado"}

@router.get("/temas")
def get_temas(curso_id: int = None, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    if curso_id: cur.execute("SELECT t.id, t.nombre, t.curso_id, t.dificultad_base, t.imagen_url, t.activo, c.nombre FROM temas t JOIN cursos c ON t.curso_id = c.id WHERE t.curso_id = %s ORDER BY t.nombre", (curso_id,))
    else: cur.execute("SELECT t.id, t.nombre, t.curso_id, t.dificultad_base, t.imagen_url, t.activo, c.nombre FROM temas t JOIN cursos c ON t.curso_id = c.id ORDER BY c.orden, t.nombre")
    rows = cur.fetchall(); conn.close()
    return [{"id": str(r[0]), "nombre": r[1], "curso_id": r[2], "dificultad_base": r[3], "imagen_url": r[4], "activo": r[5], "curso_nombre": r[6]} for r in rows]

@router.post("/temas")
def create_tema(data: TemaCreate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO temas (nombre, curso_id, dificultad_base, imagen_url) VALUES (%s, %s, %s, %s) RETURNING id", (data.nombre, data.curso_id, data.dificultad_base, data.imagen_url))
    conn.commit(); conn.close()
    return {"nombre": data.nombre}

@router.put("/temas/{tema_id}")
def update_tema(tema_id: str, data: TemaUpdate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    updates, values = [], []
    if data.nombre: updates.append("nombre = %s"); values.append(data.nombre)
    if data.curso_id: updates.append("curso_id = %s"); values.append(data.curso_id)
    if data.dificultad_base is not None: updates.append("dificultad_base = %s"); values.append(data.dificultad_base)
    if data.imagen_url is not None: updates.append("imagen_url = %s"); values.append(data.imagen_url)
    if data.activo is not None: updates.append("activo = %s"); values.append(data.activo)
    values.append(tema_id)
    cur.execute(f"UPDATE temas SET {', '.join(updates)} WHERE id = %s", values)
    conn.commit(); conn.close()
    return {"id": tema_id}

@router.delete("/temas/{tema_id}")
def delete_tema(tema_id: str, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM temas WHERE id = %s", (tema_id,))
    conn.commit(); conn.close()
    return {"message": "Tema eliminado"}

@router.get("/preguntas")
def get_preguntas(estado: str = None, tema_id: int = None, asignatura_id: int = None, solo_pendientes: bool = False, current_user: dict = Depends(require_role([1]))):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        print(f"DEBUG: estado={estado}, tema_id={tema_id}, asignatura_id={asignatura_id}")
        
        # Por defecto mostrar aprobadas
        sql = "SELECT p.id, p.tema_id, p.asignatura_id, p.enunciado, p.explicacion, p.imagen_url, p.dificultad, p.tipo_id, p.activa, COALESCE(a.nombre, t.nombre, 'Sin asignar'), COALESCE(tp.nombre, 'Estandar'), a.nombre, p.estado, p.motivo_rechazo, p.usuario_id, NULL FROM preguntas p LEFT JOIN temas t ON p.tema_id = t.id LEFT JOIN asignaturas a ON p.asignatura_id = a.id LEFT JOIN tipos_pregunta tp ON p.tipo_id = tp.id"
        
        if estado == 'aprobado':
            sql += " WHERE p.estado = 'aprobado' OR p.estado IS NULL"
        elif estado == 'pendiente':
            sql += " WHERE p.estado = 'pendiente'"
        else:
            sql += " WHERE p.estado = 'aprobado' OR p.estado IS NULL"
            
        sql += " ORDER BY p.id"
        
        print(f"DEBUG SQL: {sql[:100]}...")
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return [{"id": str(r[0]), "tema_id": r[1], "asignatura_id": r[2], "enunciado": r[3], "explicacion": r[4], "imagen_url": r[5], 
                "dificultad": r[6], "tipo_id": r[7], "activa": r[8], "tema_nombre": r[9], "tipo_nombre": r[10], 
                "asignatura_nombre": r[11], "estado": r[12], "motivo_rechazo": r[13], "usuario_id": r[14], "usuario_email": r[15]} for r in rows]
    except Exception as e:
        print(f"ERROR in get_preguntas: {e}")
        raise

@router.post("/preguntas")
def create_pregunta(data: PreguntaCreate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO preguntas (tema_id, asignatura_id, enunciado, explicacion, dificultad, tipo_id, activa, imagen_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id", (data.tema_id, data.asignatura_id, data.enunciado, data.explicacion, data.dificultad, data.tipo_id, data.activa, data.imagen_url))
    pregunta_id = cur.fetchone()[0]; conn.commit(); conn.close()
    return {"id": str(pregunta_id), "enunciado": data.enunciado}

@router.put("/preguntas/{pregunta_id}")
def update_pregunta(pregunta_id: int, data: PreguntaUpdate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    updates, values = [], []
    if data.tema_id is not None: updates.append("tema_id = %s"); values.append(data.tema_id)
    if data.asignatura_id is not None: updates.append("asignatura_id = %s"); values.append(data.asignatura_id)
    if data.enunciado: updates.append("enunciado = %s"); values.append(data.enunciado)
    if data.explicacion is not None: updates.append("explicacion = %s"); values.append(data.explicacion)
    if data.imagen_url is not None: updates.append("imagen_url = %s"); values.append(data.imagen_url)
    if data.dificultad is not None: updates.append("dificultad = %s"); values.append(data.dificultad)
    if data.tipo_id is not None: updates.append("tipo_id = %s"); values.append(data.tipo_id)
    if data.activa is not None: updates.append("activa = %s"); values.append(data.activa)
    if data.estado is not None: updates.append("estado = %s"); values.append(data.estado)
    if data.motivo_rechazo is not None: updates.append("motivo_rechazo = %s"); values.append(data.motivo_rechazo)
    values.append(pregunta_id)
    if updates:
        cur.execute(f"UPDATE preguntas SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    conn.close()
    return {"id": pregunta_id}

@router.post("/preguntas/{pregunta_id}/aprobar")
def aprobar_pregunta(pregunta_id: int, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE preguntas SET estado = 'aprobado', motivo_rechazo = NULL WHERE id = %s", (pregunta_id,))
    conn.commit()
    conn.close()
    return {"id": pregunta_id, "estado": "aprobado"}

@router.post("/preguntas/{pregunta_id}/rechazar")
def rechazar_pregunta(pregunta_id: int, motivo: str, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE preguntas SET estado = 'rechazado', motivo_rechazo = %s WHERE id = %s", (motivo, pregunta_id))
    conn.commit()
    conn.close()
    return {"id": pregunta_id, "estado": "rechazado", "motivo": motivo}

@router.delete("/preguntas/{pregunta_id}")
def delete_pregunta(pregunta_id: int, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM opciones WHERE pregunta_id = %s", (pregunta_id,))
    cur.execute("DELETE FROM preguntas WHERE id = %s", (pregunta_id,))
    conn.commit()
    conn.close()
    return {"message": "Pregunta eliminada"}

@router.get("/preguntas/{pregunta_id}/opciones")
def get_opciones(pregunta_id: int, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT id, pregunta_id, texto, es_correcta, activa FROM opciones WHERE pregunta_id = %s ORDER BY id", (pregunta_id,))
    rows = cur.fetchall(); conn.close()
    return [{"id": str(r[0]), "pregunta_id": str(r[1]), "texto": r[2], "es_correcta": r[3], "activa": r[4]} for r in rows]

@router.post("/preguntas/{pregunta_id}/opciones")
def create_opcion(pregunta_id: int, data: OpcionCreate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO opciones (pregunta_id, texto, es_correcta, activa) VALUES (%s, %s, %s, %s) RETURNING id", (pregunta_id, data.texto, data.es_correcta, data.activa))
    opcion_id = cur.fetchone()[0]; conn.commit(); conn.close()
    return {"id": str(opcion_id), "texto": data.texto}

@router.put("/opciones/{opcion_id}")
def update_opcion(opcion_id: int, data: OpcionUpdate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    updates, values = [], []
    if data.texto: updates.append("texto = %s"); values.append(data.texto)
    if data.es_correcta is not None: updates.append("es_correcta = %s"); values.append(data.es_correcta)
    if data.activa is not None: updates.append("activa = %s"); values.append(data.activa)
    values.append(opcion_id)
    if updates:
        cur.execute(f"UPDATE opciones SET {', '.join(updates)} WHERE id = %s", values)
        conn.commit()
    conn.close()
    return {"id": opcion_id}

@router.delete("/opciones/{opcion_id}")
def delete_opcion(opcion_id: int, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM opciones WHERE id = %s", (opcion_id,))
    conn.commit(); conn.close()
    return {"message": "Opcion eliminada"}

@router.get("/estadisticas")
def get_estadisticas(current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM usuarios"); total_usuarios = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM preguntas WHERE activa = TRUE"); total_preguntas = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM simulacros WHERE estado = 'finalizado'"); total_simulacros = cur.fetchone()[0]
    cur.execute("SELECT AVG(puntaje_total) FROM simulacros WHERE estado = 'finalizado'"); promedio = cur.fetchone()[0] or 0
    cur.execute("SELECT COUNT(*) FROM sesiones WHERE estado = 'activa'"); sesiones = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM cursos WHERE activo = TRUE"); cursos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM temas WHERE activo = TRUE"); temas = cur.fetchone()[0]
    conn.close()
    return {"usuarios": total_usuarios, "preguntas": total_preguntas, "simulacros": total_simulacros, "promedio": round(promedio, 1), "sesiones": sesiones, "cursos": cursos, "temas": temas}

@router.get("/bloques")
def get_bloques(current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT id, codigo, nombre, descripcion, orden, activo FROM bloques_tematicos ORDER BY orden")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "codigo": r[1], "nombre": r[2], "descripcion": r[3], "orden": r[4], "activo": r[5]} for r in rows]

@router.post("/bloques")
def create_bloque(data: BloqueCreate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO bloques_tematicos (codigo, nombre, descripcion, orden) VALUES (%s, %s, %s, %s) RETURNING id", (data.codigo, data.nombre, data.descripcion, data.orden))
    blok_id = cur.fetchone()[0]; conn.commit(); conn.close()
    return {"id": blok_id, "nombre": data.nombre}

@router.put("/bloques/{bloque_id}")
def update_bloque(bloque_id: int, data: BloqueUpdate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    updates, values = [], []
    if data.codigo: updates.append("codigo = %s"); values.append(data.codigo)
    if data.nombre: updates.append("nombre = %s"); values.append(data.nombre)
    if data.descripcion: updates.append("descripcion = %s"); values.append(data.descripcion)
    if data.orden is not None: updates.append("orden = %s"); values.append(data.orden)
    values.append(bloque_id)
    cur.execute(f"UPDATE bloques_tematicos SET {', '.join(updates)} WHERE id = %s", values); conn.commit(); conn.close()
    return {"id": bloque_id}

@router.delete("/bloques/{bloque_id}")
def delete_bloque(bloque_id: int, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM bloques_tematicos WHERE id = %s", (bloque_id,)); conn.commit(); conn.close()
    return {"message": "Bloque eliminado"}

@router.get("/areas")
def get_areas(bloque_id: int = None, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    if bloque_id: cur.execute("SELECT a.id, a.bloque_id, a.codigo, a.nombre, a.descripcion, a.orden, a.activo, b.nombre FROM areas a JOIN bloques_tematicos b ON a.bloque_id = b.id WHERE a.bloque_id = %s ORDER BY a.orden", (bloque_id,))
    else: cur.execute("SELECT a.id, a.bloque_id, a.codigo, a.nombre, a.descripcion, a.orden, a.activo, b.nombre FROM areas a JOIN bloques_tematicos b ON a.bloque_id = b.id ORDER BY a.orden")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "bloque_id": r[1], "codigo": r[2], "nombre": r[3], "descripcion": r[4], "orden": r[5], "activo": r[6], "bloque_nombre": r[7]} for r in rows]

@router.post("/areas")
def create_area(data: AreaCreate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO areas (bloque_id, codigo, nombre, descripcion, orden) VALUES (%s, %s, %s, %s, %s) RETURNING id", (data.bloque_id, data.codigo, data.nombre, data.descripcion, data.orden))
    area_id = cur.fetchone()[0]; conn.commit(); conn.close()
    return {"id": area_id, "nombre": data.nombre}

@router.put("/areas/{area_id}")
def update_area(area_id: int, data: AreaUpdate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    updates, values = [], []
    if data.bloque_id: updates.append("bloque_id = %s"); values.append(data.bloque_id)
    if data.codigo: updates.append("codigo = %s"); values.append(data.codigo)
    if data.nombre: updates.append("nombre = %s"); values.append(data.nombre)
    if data.descripcion: updates.append("descripcion = %s"); values.append(data.descripcion)
    if data.orden is not None: updates.append("orden = %s"); values.append(data.orden)
    values.append(area_id)
    cur.execute(f"UPDATE areas SET {', '.join(updates)} WHERE id = %s", values); conn.commit(); conn.close()
    return {"id": area_id}

@router.delete("/areas/{area_id}")
def delete_area(area_id: int, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM areas WHERE id = %s", (area_id,)); conn.commit(); conn.close()
    return {"message": "Area eliminada"}

@router.get("/asignaturas")
def get_asignaturas(area_id: int = None, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    if area_id: cur.execute("SELECT a.id, a.area_id, a.nombre, a.descripcion, a.orden, a.activo, ar.nombre FROM asignaturas a JOIN areas ar ON a.area_id = ar.id WHERE a.area_id = %s ORDER BY a.orden", (area_id,))
    else: cur.execute("SELECT a.id, a.area_id, a.nombre, a.descripcion, a.orden, a.activo, ar.nombre FROM asignaturas a JOIN areas ar ON a.area_id = ar.id ORDER BY a.orden")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "area_id": r[1], "nombre": r[2], "descripcion": r[3], "orden": r[4], "activo": r[5], "area_nombre": r[6]} for r in rows]

@router.post("/asignaturas")
def create_asignatura(data: AsignaturaCreate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO asignaturas (area_id, nombre, descripcion, orden) VALUES (%s, %s, %s, %s) RETURNING id", (data.area_id, data.nombre, data.descripcion, data.orden))
    asig_id = cur.fetchone()[0]; conn.commit(); conn.close()
    return {"id": asig_id, "nombre": data.nombre}

@router.put("/asignaturas/{asignatura_id}")
def update_asignatura(asignatura_id: int, data: AsignaturaUpdate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    updates, values = [], []
    if data.area_id: updates.append("area_id = %s"); values.append(data.area_id)
    if data.nombre: updates.append("nombre = %s"); values.append(data.nombre)
    if data.descripcion: updates.append("descripcion = %s"); values.append(data.descripcion)
    if data.orden is not None: updates.append("orden = %s"); values.append(data.orden)
    values.append(asignatura_id)
    cur.execute(f"UPDATE asignaturas SET {', '.join(updates)} WHERE id = %s", values); conn.commit(); conn.close()
    return {"id": asignatura_id}

@router.delete("/asignaturas/{asignatura_id}")
def delete_asignatura(asignatura_id: int, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM asignaturas WHERE id = %s", (asignatura_id,)); conn.commit(); conn.close()
    return {"message": "Asignatura eliminada"}

@router.get("/grupos-academicos")
def get_grupos_academicos(current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT id, codigo, nombre, descripcion, orden, activo FROM grupos_academicos ORDER BY orden")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "codigo": r[1], "nombre": r[2], "descripcion": r[3], "orden": r[4], "activo": r[5]} for r in rows]

@router.post("/grupos-academicos")
def create_grupo_academico(data: GrupoAcadCreate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO grupos_academicos (codigo, nombre, descripcion, orden) VALUES (%s, %s, %s, %s) RETURNING id", (data.codigo, data.nombre, data.descripcion, data.orden))
    ga_id = cur.fetchone()[0]; conn.commit(); conn.close()
    return {"id": ga_id, "nombre": data.nombre}

@router.put("/grupos-academicos/{grupo_id}")
def update_grupo_academico(grupo_id: int, data: GrupoAcadUpdate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    updates, values = [], []
    if data.codigo: updates.append("codigo = %s"); values.append(data.codigo)
    if data.nombre: updates.append("nombre = %s"); values.append(data.nombre)
    if data.descripcion: updates.append("descripcion = %s"); values.append(data.descripcion)
    if data.orden is not None: updates.append("orden = %s"); values.append(data.orden)
    values.append(grupo_id)
    cur.execute(f"UPDATE grupos_academicos SET {', '.join(updates)} WHERE id = %s", values); conn.commit(); conn.close()
    return {"id": grupo_id}

@router.delete("/grupos-academicos/{grupo_id}")
def delete_grupo_academico(grupo_id: int, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM grupos_academicos WHERE id = %s", (grupo_id,)); conn.commit(); conn.close()
    return {"message": "Grupo akademico eliminado"}

@router.get("/config-puntaje")
def get_config_puntaje(grupo_id: int = None, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    if grupo_id: cur.execute("""SELECT cp.id, cp.grupo_academico_id, cp.asignatura_id, cp.numero_preguntas, cp.puntaje_pregunta, cp.activo, ga.nombre, a.nombre FROM configuraciones_puntaje cp JOIN grupos_academicos ga ON cp.grupo_academico_id = ga.id JOIN asignaturas a ON cp.asignatura_id = a.id WHERE cp.grupo_academico_id = %s ORDER BY a.orden""", (grupo_id,))
    else: cur.execute("""SELECT cp.id, cp.grupo_academico_id, cp.asignatura_id, cp.numero_preguntas, cp.puntaje_pregunta, cp.activo, ga.nombre, a.nombre FROM configuraciones_puntaje cp JOIN grupos_academicos ga ON cp.grupo_academico_id = ga.id JOIN asignaturas a ON cp.asignatura_id = a.id ORDER BY ga.orden, a.orden""")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "grupo_academico_id": r[1], "asignatura_id": r[2], "numero_preguntas": r[3], "puntaje_pregunta": float(r[4]), "activo": r[5], "grupo_nombre": r[6], "asignatura_nombre": r[7]} for r in rows]

@router.post("/config-puntaje")
def create_config_puntaje(data: ConfigPuntajeCreate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("""INSERT INTO configuraciones_puntaje (grupo_academico_id, asignatura_id, numero_preguntas, puntaje_pregunta) VALUES (%s, %s, %s, %s) RETURNING id""", (data.grupo_academico_id, data.asignatura_id, data.numero_preguntas, data.puntaje_pregunta))
    cfg_id = cur.fetchone()[0]; conn.commit(); conn.close()
    return {"id": cfg_id}

@router.put("/config-puntaje/{config_id}")
def update_config_puntaje(config_id: int, data: ConfigPuntajeUpdate, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    updates, values = [], []
    if data.numero_preguntas is not None: updates.append("numero_preguntas = %s"); values.append(data.numero_preguntas)
    if data.puntaje_pregunta is not None: updates.append("puntaje_pregunta = %s"); values.append(data.puntaje_pregunta)
    values.append(config_id)
    cur.execute(f"UPDATE configuraciones_puntaje SET {', '.join(updates)} WHERE id = %s", values); conn.commit(); conn.close()
    return {"id": config_id}

@router.delete("/config-puntaje/{config_id}")
def delete_config_puntaje(config_id: int, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM configuraciones_puntaje WHERE id = %s", (config_id,)); conn.commit(); conn.close()
    return {"message": "Configuracion de puntaje eliminada"}

@router.get("/reportes")
def get_reportes(current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""SELECT r.id, r.pregunta_id, r.usuario_id, r.motivo, r.estado, r.fecha, p.enunciado, u.email 
                FROM reportes_preguntas r
                LEFT JOIN preguntas p ON r.pregunta_id = p.id
                LEFT JOIN usuarios u ON r.usuario_id = u.id
                ORDER BY r.fecha DESC""")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "pregunta_id": r[1], "usuario_id": r[2], "motivo": r[3], "estado": r[4], "fecha": str(r[5]), "pregunta_enunciado": r[6], "usuario_email": r[7]} for r in rows]

@router.post("/reportes/{reporte_id}/revisar")
def revisar_reporte(reporte_id: int, resolver: bool, current_user: dict = Depends(require_role([1]))):
    conn = get_db_connection()
    cur = conn.cursor()
    nuevo_estado = "resuelto" if resolver else "ignorado"
    cur.execute("UPDATE reportes_preguntas SET estado = %s WHERE id = %s", (nuevo_estado, reporte_id))
    conn.commit()
    conn.close()
    return {"id": reporte_id, "estado": nuevo_estado}


# ========== PERMISOS DE USUARIOS ==========

@router.get("/init-permisos")
async def init_permisos():
    """Inicializa la tabla de permisos."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuario_permisos (
            id SERIAL PRIMARY KEY,
            usuario_id UUID NOT NULL,
            seccion VARCHAR(50) NOT NULL,
            tiene_acceso BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(usuario_id, seccion)
        )
    """)
    
    conn.commit()
    conn.close()
    return {"message": "Tabla de permisos creada"}


@router.get("/usuarios-permisos")
async def get_usuarios_permisos(current_user: dict = Depends(require_role([1]))):
    """Obtiene todos los usuarios con sus permisos."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Obtener todos los usuarios
        cur.execute("SELECT id, nombre_completo, email, rol_id FROM usuarios ORDER BY email")
        rows = cur.fetchall()
        
        usuarios = []
        for r in rows:
            usuario_id = str(r[0])
            
            # Obtener permisos
            cur.execute("SELECT seccion, tiene_acceso FROM usuario_permisos WHERE usuario_id = %s", (usuario_id,))
            perms = cur.fetchall()
            permisos = {p[0]: p[1] for p in perms} if perms else {}
            
            usuarios.append({
                "id": usuario_id,
                "nombre": r[1] or r[2],  # nombre o email
                "email": r[2],
                "rol_id": r[3],
                "permisos": [{"seccion": k, "tiene_acceso": v} for k, v in permisos.items()]
            })
        
        conn.close()
        return usuarios
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()}


class PermisoUpdate(BaseModel):
    usuario_id: str
    seccion: str
    tiene_acceso: bool


@router.put("/usuarios-permisos")
async def update_usuario_permiso(data: PermisoUpdate, current_user: dict = Depends(require_role([1]))):
    """Actualiza el permiso de un usuario para una sección."""
    from psycopg2.extras import RealDictCursor
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        usuario_id = int(data.usuario_id)
        
        cur.execute("""
            INSERT INTO usuario_permisos (usuario_id, seccion, tiene_acceso)
            VALUES (%s, %s, %s)
            ON CONFLICT (usuario_id, seccion)
            DO UPDATE SET tiene_acceso = %s
        """, (usuario_id, data.seccion, data.tiene_acceso, data.tiene_acceso))
        
        conn.commit()
        return {"usuario_id": str(usuario_id), "seccion": data.seccion, "tiene_acceso": data.tiene_acceso}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


@router.get("/mis-permisos")
async def get_mis_permisos(credentials = Depends(http_bearer)):
    """Obtiene los permisos del usuario actual."""
    from app.core.security import decode_token
    
    if not credentials:
        return {"dashboard": False, "simulacros": False, "temas_debiles": False, "flashcards": False, "admin": False}
    
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except:
        return {"dashboard": False, "simulacros": False, "temas_debiles": False, "flashcards": False, "admin": False}
    
    user_id = payload.get("sub")
    if not user_id:
        return {"dashboard": False, "simulacros": False, "temas_debiles": False, "flashcards": False, "admin": False}
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get rol_id del usuario
        cur.execute("SELECT rol_id FROM usuarios WHERE id = %s", (user_id,))
        user_row = cur.fetchone()
        rol_id = user_row[0] if user_row else 2
        
        # Admin (rol_id=1) tiene todos los permisos
        if rol_id == 1:
            return {"dashboard": True, "simulacros": True, "temas_debiles": True, "flashcards": True, "feynman": True, "admin": True}
        
        # Get permisos de la DB
        cur.execute("SELECT seccion, tiene_acceso FROM usuario_permisos WHERE usuario_id = %s", (user_id,))
        rows = cur.fetchall()
        permisos = {r[0]: r[1] for r in rows}
        conn.close()
        
        if not permisos:
            # Default para usuarios sin permisos definidos
            return {"dashboard": True, "simulacros": True, "temas_debiles": True, "flashcards": True, "feynman": True, "admin": False}
        
        return permisos
    except:
        return {"dashboard": True, "simulacros": True, "temas_debiles": True, "flashcards": True, "feynman": True, "admin": False}