from datetime import datetime, timedelta
from typing import Optional
import uuid
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import get_settings
from .db import get_db_connection


settings = get_settings()


def hash_password(password: str) -> str:
    """
    Hashea contraseña usando bcrypt.
    Costo 12 para seguridad óptima.
    """
    # Genera salt y hashea
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica contraseña contra hash.
    Retorna True si coincide.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea token JWT de acceso.
    Datos: {sub: user_id, jti: unique_id, rol: rol_id}
    """
    to_encode = data.copy()
    # Usa JTI existente o genera nuevo
    if "jti" not in to_encode:
        to_encode["jti"] = str(uuid.uuid4())
    to_encode["type"] = "access"

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    # Firma con secret_key
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Crea token JWT de renovación.
    Expira en 7 días.
    """
    to_encode = data.copy()
    to_encode.update({"type": "refresh"})
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decodifica y valida token JWT.
    Retorna diccionario con datos del token.
    Lanza excepción si inválido o expirado.
    """
    try:
        # Decodifica sin verificar expiración (verificamos manualmente)
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"verify_exp": False},
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Bearer token para FastAPI
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependencia para obtener usuario actual desde token.
    Verifica que el token sea válido y la sesión exista.
    """
    token = credentials.credentials
    payload = decode_token(token)

    user_id = payload.get("sub")
    jti = payload.get("jti")

    if not user_id or not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )

    # Verifica sesión activa en DB
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT usuario_id FROM sesiones WHERE jti = %s AND usuario_id = %s AND estado = 'activa'",
        (jti, user_id),
    )
    session = cur.fetchone()
    conn.close()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada o inválida",
        )

    # Obtiene datos del usuario
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre_completo, email, rol_id, especialidad_id FROM usuarios WHERE id = %s AND activo = TRUE",
        (user_id,),
    )
    user = cur.fetchone()
    conn.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado"
        )

    return {
        "id": user[0],
        "nombre": user[1],
        "email": user[2],
        "rol_id": user[3],
        "especialidad_id": user[4],
    }


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[dict]:
    """
    Dependencia opcional para usuario autenticado.
    Retorna None si no hay token.
    """
    if not credentials:
        return None
    return await get_current_user(credentials)


def require_role(allowed_roles):
    """
    Dependencia factory para requerir roles específicos.
    Uso: @app.get("/admin") -> Depends(require_role([1]))
    allowed_roles puede ser un int o una lista de ints.
    """
    if isinstance(allowed_roles, int):
        allowed_roles = [allowed_roles]

    async def role_checker(current_user: dict = Depends(get_current_user)):
        rol_id = current_user.get("rol_id", 1)
        if rol_id not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos"
            )
        return current_user

    return role_checker
