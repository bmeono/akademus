import os
import json
import urllib.request
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.security import get_ current_ user
from app. core. db import get_ db_ connection
router = APIRouter( prefix="/comunidad", tags=["comunidad"])  # routes
GEMINI_ API_ KEY = os. getenv("GEMINI_ API_ KEY")  # API key
SYSTEM_ PROMPT = "Eres el Tutor Virtual de AKADEMUS. Resuelve dudas academicas de manera pedagogica."  # prompt
class ConsultaRequest( BaseModel):  # model
    materia: str
    pregunta: str
async def llamar_ gemini( pregunta: str) -> str:  # llama a gemini
    if not GEMINI_ API_ KEY:  # check API key
        raise HTTPException( status_ code=500, detail="API Key de Gemini no configurada.")  # error
    url = f"https://generativelanguage. googleapis. com/ v1/ models/ gemini-1.5- flash: generateContent? key={GEMINI_ API_ KEY}"  # url
    payload = {  # payload
        "contents": [{"parts": [{"text": f"{SYSTEM_ PROMPT}\n\ nPregunta:\n{pregunta}"}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }
    data = json. dumps(payload). encode("utf-8")  # data
    req = urllib. request. Request( url, data=data, headers={"Content- Type": "application/ json"})  # request
    try:  # try
        response = urllib. request. urlopen( req, timeout=60)  # response
        result = json. loads( response. read(). decode("utf-8"))  # result
        return result["candidates"][0]["content"]["parts"][0]["text"]  # return
    except Exception as e:  # except
        raise HTTPException( status_ code=500, detail=f"Error en comunicacion con Gemini: {str(e)}")  # error
@router. get("/asignaturas")  # get asignaturas
async def get_ asignaturas( current_ user: dict = Depends( get_ current_ user)):  # get asignaturas
    conn = get_ db_ connection()  # connection
    cur = conn. cursor()  # cursor
    cur. execute( "SELECT id, nombre FROM asignaturas ORDER BY orden, nombre")  # query
    rows = cur. fetchall()  # rows
    conn. close()  # close
    return {"asignaturas": [{"id": r[0], "nombre": r[1]} for r in rows]}  # return
@router. post("/consultar")  # post consultar
async def hacer_ consulta( req: ConsultaRequest, current_ user: dict = Depends( get_ current_ user)):  # hacer consulta
    user_ id = current_ user["id"]  # user id
    conn = get_ db_ connection()  # connection
    cur = conn. cursor()  # cursor
    cur. execute( "SELECT consultas_ia_ Disponibles FROM usuarios WHERE id = %s", ( str( user_ id),))  # query
    row = cur. fetchone()  # row
    if not row:  # check
        conn. close()  # close
        raise HTTPException( status_ code=404, detail="Usuario no encontrado")  # error
    creditos = row[0] if row[0] else 0  # creditos
    if creditos <= 0:  # check
        conn. close()  # close
        raise HTTPException( status_ code=403, detail="Sin creditos disponibles")  # error
    try:  # try
        respuesta = await llamar_ gemini( req. pregunta)  # respuesta
    except Exception as e:  # except
        conn. close()  # close
        raise HTTPException( status_ code=500, detail=str(e))  # error
    cur. execute(  # insert
        "INSERT INTO comunidad_ consultas ( usuario_ id, materia, pregunta, respuesta) VALUES (%s, %s, %s, %s)",
        ( user_ id, req. materia, req. pregunta, respuesta)
    )
    cur. execute(  # update
        "UPDATE usuarios SET consultas_ia_ Disponibles = consultas_ia_ Disponibles - 1 WHERE id = %s",
        ( str( user_ id),)
    )
    conn. commit()  # commit
    conn. close()  # close
    return {"respuesta": respuesta}  # return
@router. get("/historial")  # get historial
async def get_ historial( current_ user: dict = Depends( get_ current_ user)):  # get historial
    user_ id = current_ user["id"]  # user id
    try:  # try
        conn = get_ db_ connection()  # connection
        cur = conn. cursor()  # cursor
        cur. execute(  # query
            "SELECT id, materia, pregunta, respuesta, fecha_ consulta FROM comunidad_ consultas WHERE usuario_ id = %s ORDER BY fecha_ consulta DESC LIMIT 50",
            ( str( user_ id),)
        )
        rows = cur. fetchall()  # rows
        conn. close()  # close
        return {"historial": [{"id": r[0], "materia": r[1], "pregunta": r[2], "respuesta": r[3], "fecha": r[4]} for r in rows]}  # return
    except Exception as e:  # except
        return {"historial": [], "error": str(e)}  # error
@router. get("/creditos")  # get creditos
async def get_ creditos( current_ user: dict = Depends( get_ current_ user)):  # get creditos
    user_ id = current_ user["id"]  # user id
    conn = get_ db_ connection()  # connection
    cur = conn. cursor()  # cursor
    cur. execute( "SELECT consultas_ia_ Disponibles FROM usuarios WHERE id = %s", ( str( user_ id),))  # query
    row = cur. fetchone()  # row
    conn. close()  # close
    return {"creditos": row[0] if row and row[0] else 0}  # return