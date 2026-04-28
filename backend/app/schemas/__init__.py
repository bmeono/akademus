from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Auth Schemas


class UserRegister(BaseModel):
    nombre_completo: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    telefono: str = Field(..., pattern=r"^\+?[\d]{9,15}$")
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class OTPVerify(BaseModel):
    codigo: str = Field(..., min_length=6, max_length=6)
    temp_token: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TempTokenResponse(BaseModel):
    requires_2fa: bool = True
    temp_token: str


# User Schemas


class UserResponse(BaseModel):
    id: str
    nombre_completo: str
    email: str
    telefono: Optional[str] = None
    rol_id: int
    especialidad_id: Optional[int]
    two_factor_enabled: bool
    fecha_registro: datetime
    ultimo_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    especialidad_id: Optional[int] = None


class EspecialidadResponse(BaseModel):
    id: int
    nombre: str
    grupo_id: int
    puntaje_minimo: int

    class Config:
        from_attributes = True


class GrupoEspecialidadResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    orden: int

    class Config:
        from_attributes = True


# Preguntas Schemas


class PreguntaResponse(BaseModel):
    id: int
    tema_id: int
    enunciado: str
    explicacion: Optional[str]
    imagen_url: Optional[str]
    dificultad: int

    class Config:
        from_attributes = True


class OpcionResponse(BaseModel):
    id: int
    pregunta_id: int
    texto: str

    class Config:
        from_attributes = True


class PreguntaCompletaResponse(BaseModel):
    pregunta: PreguntaResponse
    opciones: List[OpcionResponse]

    class Config:
        from_attributes = True


# Simulacro Schemas


class SimulacroConfig(BaseModel):
    curso_ids: List[int] = Field(..., min_items=1)
    tema_ids: Optional[List[int]] = None
    num_preguntas: int = Field(default=10, ge=5, le=50)
    duracion_minutos: int = Field(default=30, ge=5, le=120)


class SimulacroEspecialidadConfig(BaseModel):
    especialidad_id: Optional[int] = None


class SimulacroStartResponse(BaseModel):
    simulacro_id: int
    total_preguntas: int
    duracion_segundos: int


class RespuestaEnviar(BaseModel):
    pregunta_id: int
    opcion_seleccionada_id: int
    tiempo_respuesta_segundos: float


class RespuestaResultResponse(BaseModel):
    es_correcta: bool
    explicacion: Optional[str]
    siguiente_pregunta: Optional[PreguntaCompletaResponse]


class SimulacroResultResponse(BaseModel):
    id: int
    puntaje_total: float
    total_preguntas: int
    aciertos: int
    errores: int
    sin_responder: int
    tiempo_total_segundos: float


# Flashcard Schemas


class FlashcardReviewResponse(BaseModel):
    id: int
    frente: str
    dorso: str
    imagen_frente: Optional[str]
    imagen_dorso: Optional[str]

    class Config:
        from_attributes = True


class FlashcardCalificar(BaseModel):
    calidad: str = Field(..., pattern=r"^(difficult|good|easy)$")


class FlashcardStatsResponse(BaseModel):
    total_hoy: int
    repasadas_hoy: int
    total_todas: int
    intervalo_promedio: float


# Feynman Schemas


class FeynmanExplicacion(BaseModel):
    tema_id: int
    explicacion: str = Field(..., min_length=100)


class FeynmanResponse(BaseModel):
    id: int
    tema_id: int
    explicacion_usuario: str
    puntaje_admin: Optional[int]
    comentario_admin: Optional[str]
    estado: str
    fecha_creacion: datetime
    fecha_revision: Optional[datetime]

    class Config:
        from_attributes = True


class FeynmanCalificar(BaseModel):
    puntaje: int = Field(..., ge=0, le=100)
    comentario: Optional[str] = None
    estado: str = Field(..., pattern=r"^(revisado|aprobado|refuerzo)$")


# Dashboard Schemas


class DashboardResumen(BaseModel):
    racha_dias: int
    promedio_aciertos: float
    total_preguntas_respondidas: int
    total_flashcards_repasadas: int
    temas_debiles: List[dict]


class EvolucionData(BaseModel):
    semana: str
    promedio_aciertos: float


class TemaDebilResponse(BaseModel):
    tema_id: int
    nombre: str
    porcentaje_aciertos: float


# Error Schemas


class ErrorResponse(BaseModel):
    detail: str
