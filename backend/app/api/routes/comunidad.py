from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.security import get_current_user
from app.core.db import get_db_connection
router = APIRouter(prefix="/comunidad", tags=["comunidad"])
GEMINI_API_KEY = "AIzaSyAMfa91FpMEqNgs4rKuP5hX2ypqhB7Ib3Y"
SYSTEM_PROMPT = "Eres el Tutor Virtual de AKADEMUS. Resuelve dudas academicas de manera pedagogica."
class ConsultaRequest(BaseModel):
    materia: str
    pregunta: str
async def llamar_gemini(pregunta: str) -> str:
    import urllib.request
    import json
    url = "https://generativelanguage.googleapis.com/v1/odels/gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY
    payload = {"contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\nPregunta:\n" + pregunta}]}], "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        response = urllib.request.urlopen(req, timeout=60)
        result = json.loads(response.read().decode("utf-8"))
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error Gemini: " + str(e))
@router.get("/asignaturas")
async def get_asignaturas(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM asignaturas ORDER BY orden, nombre")
    rows = cur.fetchall()
    conn.close()
    return {"asignaturas": [{"id": r[0], "nombre": r[1]} for r in rows]}
@router.post("/consultar")
async def hacer_consulta(req: ConsultaRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT consultas_ia_disponibles FROM usuarios WHERE id = %s", (str(user_id),))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    creditos = row[0] if row[0] else 0
    if creditos <= 0:
        conn.close()
        raise HTTPException(status_code=403, detail="Sin creditos disponibles")
    try:
        respuesta = await llamar_gemini(req.pregunta)
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    cur.execute("INSERT INTO comunidad_consultas (usuario_id, materia, pregunta, respuesta) VALUES (%s, %s, %s, %s)", (user_id, req.materia, req.pregunta, respuesta))
    cur.execute("UPDATE usuarios SET consultas_ia_disponibles = consultas_ia_disponibles - 1 WHERE id = %s", (str(user_id),))
    conn.commit()
    conn.close()
    return {"respuesta": respuesta}
@router.get("/historial")
async def get_historial(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, materia, pregunta, respuesta, fecha_consulta FROM comunidad_consultas WHERE usuario_id = %s ORDER BY fecha_consulta DESC LIMIT 50", (str(user_id),))
        rows = cur.fetchall()
        conn.close()
        return {"historial": [{"id": r[0], "materia": r[1], "pregunta": r[2], "respuesta": r[3], "fecha": r[4]} for r in rows]}
    except Exception as e:
        return {"historial": [], "error": str(e)}
@router.get("/creditos")
async def get_creditos(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT consultas_ia_disponibles FROM usuarios WHERE id = %s", (str(user_id),))
    row = cur.fetchone()
    conn.close()
    return {"creditos": row[0] if row and row[0] else 0}