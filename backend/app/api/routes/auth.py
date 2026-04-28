import random
import string
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import RedirectResponse
from psycopg2 import connect
import sys

sys.path.insert(0, "C:/Users/Brian/Desktop/akademus/backend")

from app.core.config import get_settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.schemas import (
    UserRegister,
    UserLogin,
    OTPVerify,
    TokenResponse,
    TempTokenResponse,
    ErrorResponse,
)


settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Autenticación"])


def get_db_connection():
    """Obtiene conexión a PostgreSQL."""
    return connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )


def generar_codigo_otp() -> str:
    """Genera código OTP de 6 dígitos."""
    return "".join(random.choices(string.digits, k=6))


def hash_otp(codigo: str) -> str:
    """Hashea código OTP."""
    return hash_password(codigo)


def send_sms(telefono: str, codigo: str):
    """
    Envía SMS con código OTP.
    En desarrollo, solo loguea el código.
    """
    print(f"[DEV] SMS enviado a {telefono}: Tu código de verificación es {codigo}")
    # En producción: usar Twilio
    # client.messages.create(to=telefono, from_=settings.twilio_phone_number, body=codigo)


@router.post("/register", response_model=TempTokenResponse)
async def register(user_data: UserRegister):
    """
    Registro de usuario.
    1. Valida email/teléfono únicos.
    2. Genera código OTP.
    3. Envía SMS.
    4. Retorna temporal token.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Verifica email único
    cur.execute("SELECT id FROM usuarios WHERE email = %s", (user_data.email,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )

    # Verifica teléfono único
    cur.execute("SELECT id FROM usuarios WHERE telefono = %s", (user_data.telefono,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El teléfono ya está registrado",
        )

    # Hashea contraseña
    password_hash = hash_password(user_data.password)

    # Crea registro temporal de usuario (no confirmado)
    cur.execute(
        """
        INSERT INTO usuarios (nombre_completo, email, telefono, password_hash, two_factor_enabled)
        VALUES (%s, %s, %s, %s, TRUE)
        RETURNING id
    """,
        (user_data.nombre_completo, user_data.email, user_data.telefono, password_hash),
    )
    user_id = cur.fetchone()[0]

    # Genera código OTP
    codigo = generar_codigo_otp()
    codigo_hash = hash_otp(codigo)

    # Guarda código OTP
    expira = datetime.utcnow() + timedelta(minutes=settings.otp_expire_minutes)
    cur.execute(
        """
        INSERT INTO codigos_otp (usuario_id, codigo_hash, metodo, expira_en)
        VALUES (%s, %s, 'sms', %s)
    """,
        (user_id, codigo_hash, expira),
    )

    # Registra en auditoría
    cur.execute(
        """
        INSERT INTO auditoria_accesos (usuario_id, evento, detalles)
        VALUES (%s, 'registro', %s)
    """,
        (user_id, f'{{"email": "{user_data.email}"}}'),
    )

    conn.commit()
    conn.close()

    # En desarrollo: muestra código
    print(f"[DEV] Código OTP para {user_data.email}: {codigo}")

    # Envía SMS (simulado)
    send_sms(user_data.telefono, codigo)

    # Crea token temporal
    temp_token = create_access_token({"sub": str(user_id)})

    return TempTokenResponse(requires_2fa=True, temp_token=temp_token)


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(data: OTPVerify, current_user: dict = Depends(get_current_user)):
    """
    Verifica código OTP del registro.
    Confirma usuario y retorna tokens.
    """
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Busca código OTP válido
    cur.execute(
        """
        SELECT id, codigo_hash, expira_en, usado, intentos_fallidos
        FROM codigos_otp
        WHERE usuario_id = %s AND metodo = 'sms' AND usado = FALSE
        ORDER BY id DESC LIMIT 1
    """,
        (user_id,),
    )
    otp_record = cur.fetchone()

    if not otp_record:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No hay código pendiente"
        )

    otp_id, codigo_hash, expira, usado, intentos = otp_record

    # Verifica intentos
    if intentos >= settings.otp_max_attempts:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Demasiados intentos fallidos",
        )

    # Verifica expiración
    if datetime.utcnow() > expira:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Código expirado"
        )

    # Verifica código
    if not verify_password(data.codigo, codigo_hash):
        cur.execute(
            "UPDATE codigos_otp SET intentos_fallidos = intentos_fallidos + 1 WHERE id = %s",
            (otp_id,),
        )
        conn.commit()
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Código incorrecto"
        )

    # Marca código como usado
    cur.execute("UPDATE codigos_otp SET usado = TRUE WHERE id = %s", (otp_id,))

    # Actualiza último login
    cur.execute(
        "UPDATE usuarios SET ultimo_login = %s WHERE id = %s",
        (datetime.utcnow(), user_id),
    )

    # Registra en auditoría
    cur.execute(
        """
        INSERT INTO auditoria_accesos (usuario_id, evento)
        VALUES (%s, 'verificacion_otp')
    """,
        (user_id,),
    )

    conn.commit()
    conn.close()

    # Crea tokens
    access_token = create_access_token({"sub": str(user_id), "jti": str(user_id)})
    refresh_token = create_refresh_token({"sub": str(user_id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login")
async def login(credentials: UserLogin):
    """
    Login.
    Si 2FA enabled: retorna temp_token para verificar código.
    Si 2FA disabled: retorna tokens directos.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Busca usuario
    cur.execute(
        "SELECT id, password_hash, activo, two_factor_enabled FROM usuarios WHERE email = %s",
        (credentials.email,),
    )
    user = cur.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    user_id, password_hash, activo, two_factor_enabled = user

    if not activo:
        raise HTTPException(status_code=401, detail="Cuenta inactiva")

    if not verify_password(credentials.password, password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Si 2FA disabled, devolver tokens directamente
    if not two_factor_enabled:
        conn = get_db_connection()
        cur = conn.cursor()

        # Crear sesión con JTI único
        jti = str(uuid.uuid4())
        expira = datetime.utcnow() + timedelta(days=7)
        cur.execute(
            "INSERT INTO sesiones (jti, usuario_id, expira_en, estado) VALUES (%s, %s, %s, 'activa')",
            (jti, user_id, expira),
        )
        cur.execute(
            "UPDATE usuarios SET ultimo_login = %s WHERE id = %s",
            (datetime.utcnow(), user_id),
        )
        cur.execute(
            "INSERT INTO auditoria_accesos (usuario_id, evento) VALUES (%s, 'login')",
            (user_id,),
        )
        conn.commit()
        conn.close()

        access_token = create_access_token({"sub": str(user_id), "jti": jti})
        refresh_token = create_refresh_token({"sub": str(user_id)})
        print(f"[DEV] Login sin 2FA: {credentials.email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    # 2FA enabled - registrar y devolver temp_token
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO auditoria_accesos (usuario_id, evento) VALUES (%s, 'login')",
        (user_id,),
    )
    conn.commit()
    conn.close()

    temp_token = create_access_token({"sub": str(user_id)})
    print(f"[DEV] Login requiere 2FA: {credentials.email}")
    return {"requires_2fa": True, "temp_token": temp_token}


@router.get("/google")
async def google_login():
    """Inicia el flujo de Google OAuth."""
    import httpx
    
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth no configurado")
    
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": "https://www.akademus.online/auth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    
    url = f"{google_auth_url}?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    from fastapi import Response
    return Response(status_code=302, headers={"Location": url})


@router.get("/google/callback")
async def google_callback(code: str = None, error: str = None):
    """Callback de Google OAuth."""
    print(f"[GOOGLE_CALLBACK] code={code[:20] if code else None}..., error={error}")
    
    if error or not code:
        return RedirectResponse(url="/login?error=google_auth_failed")
    
    try:
        import httpx
        import asyncio
        
        # Intercambia code por tokens
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "https://www.akademus.online/auth/google/callback",
        }
        
        print(f"[GOOGLE_CALLBACK] Exchanging code for token...")
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=data, timeout=30.0)
            print(f"[GOOGLE_CALLBACK] Token response status: {token_response.status_code}")
            
            if token_response.status_code != 200:
                print(f"[GOOGLE_CALLBACK] Token exchange failed: {token_response.text}")
                return RedirectResponse(url="/login?error=token_exchange_failed")
            
            tokens = token_response.json()
            access_token_google = tokens.get("access_token")
            
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            user_response = await client.get(user_info_url, headers={"Authorization": f"Bearer {access_token_google}"}, timeout=30.0)
            user_info = user_response.json()
        
        email = user_info.get("email")
        nombre = user_info.get("name", email.split("@")[0])
        google_id = user_info.get("id")
        
        print(f"[GOOGLE_CALLBACK] User info: {email}")
        
        if not email:
            return RedirectResponse(url="/login?error=no_email")
    except Exception as e:
        print(f"[GOOGLE_CALLBACK] Error: {e}")
        return RedirectResponse(url="/login?error=google_callback_error")
    
    # Busca o crea usuario
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, password_hash, activo, two_factor_enabled FROM usuarios WHERE email = %s", (email,))
    user = cur.fetchone()
    
    if not user:
        user_id = str(uuid.uuid4())
        password_hash = hash_password(f"google_{google_id}_{email}")
        cur.execute(
            """INSERT INTO usuarios (id, email, nombre_completo, password_hash, rol_id, activo, fecha_registro)
            VALUES (%s, %s, %s, %s, 2, TRUE, NOW())""",
            (user_id, email, nombre, password_hash),
        )
        conn.commit()
        
        cur.execute("SELECT id, activo, two_factor_enabled FROM usuarios WHERE id = %s", (user_id,))
        user = cur.fetchone()
    
    conn.close()
    
    if not user or not user[1]:
        return RedirectResponse(url="/login?error=account_inactive")
    
    user_id, activo, two_factor_enabled = user[0], user[1], user[2]
    
    if not activo:
        return RedirectResponse(url="/login?error=account_inactive")
    
    access_token = create_access_token({"user_id": user_id, "email": email, "type": "access"})
    refresh_token = create_refresh_token({"user_id": user_id, "type": "refresh"})
    
    return RedirectResponse(
        url=f"/login?access_token={access_token}&refresh_token={refresh_token}&google_login=true"
    )


@router.post("/verify-2fa", response_model=TokenResponse)
async def verify_2fa(data: OTPVerify):
    """
    Login - Paso 2.
    Verifica 2FA y retorna tokens.
    """
    # Decodifica temp_token
    payload = decode_token(data.temp_token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )

    conn = get_db_connection()
    cur = conn.cursor()

    # Busca código OTP
    cur.execute(
        """
        SELECT id, codigo_hash, expira_en, usado, intentos_fallidos
        FROM codigos_otp
        WHERE usuario_id = %s AND metodo = 'sms' AND usado = FALSE
        ORDER BY id DESC LIMIT 1
    """,
        (user_id,),
    )
    otp_record = cur.fetchone()

    if not otp_record:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No hay código pendiente"
        )

    otp_id, codigo_hash, expira, usado, intentos = otp_record

    if intentos >= settings.otp_max_attempts:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Demasiados intentos fallidos",
        )

    if datetime.utcnow() > expira:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Código expirado"
        )

    # Verifica código
    if not verify_password(data.codigo, codigo_hash):
        cur.execute(
            "UPDATE codigos_otp SET intentos_fallidos = intentos_fallidos + 1 WHERE id = %s",
            (otp_id,),
        )
        conn.commit()
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Código incorrecto"
        )

    # Marca código usado
    cur.execute("UPDATE codigos_otp SET usado = TRUE WHERE id = %s", (otp_id,))

    # Busca sesión activa y la invalida (sesión única)
    cur.execute(
        """
        UPDATE sesiones SET estado = 'terminada'
        WHERE usuario_id = %s AND estado = 'activa'
    """,
        (user_id,),
    )

    # Crea nueva sesión
    jti = str(user_id)
    expira = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    cur.execute(
        """
        INSERT INTO sesiones (jti, usuario_id, expira_en, estado)
        VALUES (%s, %s, %s, 'activa')
    """,
        (jti, user_id, expira),
    )

    # Actualiza último login
    cur.execute(
        "UPDATE usuarios SET ultimo_login = %s WHERE id = %s",
        (datetime.utcnow(), user_id),
    )

    # Registra en auditoría
    cur.execute(
        """
        INSERT INTO auditoria_accesos (usuario_id, evento)
        VALUES (%s, 'login_exitoso')
    """,
        (user_id,),
    )

    conn.commit()
    conn.close()

    # Crea tokens
    access_token = create_access_token({"sub": str(user_id), "jti": jti})
    refresh_token = create_refresh_token({"sub": str(user_id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Renueva access token usando refresh token.
    """
    user_id = current_user["id"]

    # Crea nuevos tokens
    jti = str(user_id)
    access_token = create_access_token({"sub": str(user_id), "jti": jti})
    refresh_token = create_refresh_token({"sub": str(user_id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Cierra sesión actual.
    """
    user_id = current_user["id"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Invalida sesión
    cur.execute(
        """
        UPDATE sesiones SET estado = 'terminada'
        WHERE usuario_id = %s AND estado = 'activa'
    """,
        (user_id,),
    )

    # Registra logout
    cur.execute(
        """
        INSERT INTO auditoria_accesos (usuario_id, evento)
        VALUES (%s, 'logout')
    """,
        (user_id,),
    )

    conn.commit()
    conn.close()

    return {"message": "Sesión cerrada"}
