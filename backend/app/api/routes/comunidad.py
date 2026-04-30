from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.security import get_ current_ user
from app. core.db import get_db_ connection
router = APIRouter(prefix="/comunidad", tags=["comunidad"]) 
GEMINI_ API_ KEY = "AIzaSyAMfa91FpMEqNgs4rKuP5hX2ypqhB7Ib3Y" 
SYSTEM_ PROMPT = "Eres el Tutor Virtual de AKADEMUS."
class ConsultaRequest(BaseModel): 
    materia: str 
    pregunta: str 
async def llamar_ gemini(pregunta: str) -> str: 
    import urllib. request 
    import json 
    print(f"API_KEY length: {len(GEMINI_ API_ KEY)}") 
    url = f"https://generativelanguage. googleapis.com/ v1/models/gemini-2.0- flash:generateContent?key={GEMINI_ API_ KEY}" 
    print(f"Calling URL: {url}") 
    payload = { 
        "contents": [{"parts": [{"text": SYSTEM_ PROMPT + "\n\ nPregunta:\n" + pregunta}]}], 
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048} 
    } 
    data = json.dumps(payload). encode("utf-8") 
    req = urllib. request. Request(url, data=data, headers={"Content-Type": "application/json"}) 
    try: 
        response = urllib. request.urlopen(req, timeout=60) 
        result = json.loads(response. read(). decode("utf-8")) 
        return result["candidates"][0]["content"]["parts"][0]["text"] 
    except Exception as e: 
        print(f"Error: {str(e)}") 
        raise HTTPException(status_code=500, detail="Error Gemini: " + str(e)) 
@router.get("/asignaturas") 
async def get_ asignaturas(current_ user: dict = Depends(get_ current_ user)): 
    conn = get_db_ connection() 
    cur = conn.cursor() 
    cur.execute("SELECT id, nombre FROM asignaturas ORDER BY orden, nombre") 
    rows = cur.fetchall() 
    conn.close() 
    return {"asignaturas": [{"id": r[0], "nombre": r[1]} for r in rows]} 
@router.post("/consultar") 
async def hacer_ consulta(req: ConsultaRequest, current_ user: dict = Depends(get_ current_ user)): 
    user_ id = current_ user["id"] 
    conn = get_db_ connection() 
    cur = conn.cursor() 
    cur.execute("SELECT consultas_ia_ Disponibles FROM usuarios WHERE id = %s", (str(user_ id),)) 
    row = cur. fetchone() 
    if not row: 
        conn.close() 
        raise HTTPException(status_code=404, detail="Usuario no encontrado") 
    creditos = row[0] if row[0] else 0 
    if creditos <= 0: 
        conn.close() 
        raise HTTPException(status_code=403, detail="Sin creditos disponibles") 
    respuesta = await llamar_ gemini(req.pregunta) 
    cur.execute("INSERT INTO comunidad_ consultas (usuario_ id, materia, pregunta, respuesta) VALUES (%s, %s, %s, %s)", (user_ id, req.materia, req.pregunta, respuesta)) 
    cur.execute("UPDATE usuarios SET consultas_ia_ Disponibles = consultas_ia_ Disponibles - 1 WHERE id = %s", (str(user_ id),)) 
    conn.commit() 
    conn.close() 
    return {"respuesta": respuesta} 
@router.get("/historial") 
async def get_ historial(current_ user: dict = Depends(get_ current_ user)): 
    user_ id = current_ user["id"] 
    try: 
        conn = get_db_ connection() 
        cur = conn.cursor() 
        cur.execute("SELECT id, materia, pregunta, respuesta, fecha_ consulta FROM comunidad_ consultas WHERE usuario_ id = %s ORDER BY fecha_ consulta DESC LIMIT 50", (str(user_ id),)) 
        rows = cur.fetchall() 
        conn.close() 
        return {"historial": [{"id": r[0], "materia": r[1], "pregunta": r[2], "respuesta": r[3], "fecha": r[4]} for r in rows]} 
    except Exception as e: 
        return {"historial": [], "error": str(e)} 
@router.get("/creditos") 
async def get_ creditos(current_ user: dict = Depends(get_ current_ user)): 
    user_ id = current_ user["id"] 
    conn = get_db_ connection() 
    cur = conn.cursor() 
    cur.execute("SELECT consultas_ia_ Disponibles FROM usuarios WHERE id = %s", (str(user_ id),)) 
    row = cur.fetchone() 
    conn.close() 
    return {"creditos": row[0] if row and row[0] else 0}