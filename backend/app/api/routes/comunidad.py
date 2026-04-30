import os
import json
import traceback
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.security import get_current_user
from app.core.db import get_db_connection

router = APIRouter(prefix="/comunidad", tags=["comunidad"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
SYSTEM_PROMPT = "Eres el Tutor Virtual de AKADEMUS. Resuelve dudas academicas de manera pedagogica."

class ConsultaRequest(BaseModel):
    materia: str
    pregunta: str

async def llamar_gemini(pregunta: str) -> str:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="API Key de Gemini no configurada en el servidor.")

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nPregunta:\n{pregunta}"}]}], 
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            print(f"DEBUG Gemini status: {response.status_code}", flush=True)
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except httpx.HTTPStatusError as e:
        print(f"DEBUG Gemini HTTP error: {e.response.status_code} - {e.response.text}", flush=True)
        raise HTTPException(status_code=500, detail=f"Error de Gemini: {e.response.text}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error en comunicación con Gemini: {str(e)}")

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
    try:
        user_id = current_user["id"]
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT consultas_ia_disponibles FROM usuarios WHERE id = %s", (str(user_id),))
        row = cur.fetchone()
        print(f"DEBUG creditos row: {row}", flush=True)
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        creditos = row[0] if row[0] else 0
        if creditos <= 0:
            conn.close()
            raise HTTPException(status_code=403, detail="Sin creditos disponibles")
            
        respuesta = await llamar_gemini(req.pregunta)
        print(f"DEBUG Gemini respondió OK", flush=True)
        
        cur.execute(
            "INSERT INTO comunidad_consultas (usuario_id, materia, pregunta, respuesta) VALUES (%s, %s, %s, %s)", 
            (user_id, req.materia, req.pregunta, respuesta)
        )
        cur.execute(
            "UPDATE usuarios SET consultas_ia_disponibles = consultas_ia_disponibles - 1 WHERE id = %s", 
            (str(user_id),)
        )
        conn.commit()
        conn.close()
        return {"respuesta": respuesta}
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historial")
async def get_historial(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, materia, pregunta, respuesta, fecha_consulta FROM comunidad_consultas WHERE usuario_id = %s ORDER BY fecha_consulta DESC LIMIT 50", 
            (str(user_id),)
        )
        rows = cur.fetchall()
        conn.close()
        return {"historial": [{"id": r[0], "materia": r[1], "pregunta": r[2], "respuesta": r[3], "fecha": r[4]} for r in rows]}
    except Exception as e:
        traceback.print_exc()
        return {"historial": [], "error": str(e)}

@router.get("/creditos")
async def get_creditos(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT consultas_ia_disponibles FROM usuarios WHERE id = %s", (str(user_id),))
        row = cur.fetchone()
        conn.close()
        return {"creditos": row[0] if row and row[0] else 0}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
