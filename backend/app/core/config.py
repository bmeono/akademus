import os
from pydantic_settings import BaseSettings
from functools import lru_cache


def parse_database_url(url: str = None):
    """Parse DATABASE_URL to extract connection parameters."""
    if not url:
        return None
    # Remove query params
    url = url.split("?")[0]
    # postgres://user:pass@host:port/dbname
    if "://" not in url:
        return None
    parts = url.replace("postgres://", "").split("@")
    if len(parts) != 2:
        return None
    auth, host_db = parts
    user, pass_ = auth.split(":")
    if "/" in host_db:
        host_port, dbname = host_db.rsplit("/", 1)
        if ":" in host_port:
            host, port = host_port.rsplit(":", 1)
            port = int(port)
        else:
            host = host_port
            port = 5432
    else:
        host = host_db
        port = 5432
        dbname = "postgres"
    return {"host": host, "port": port, "user": user, "password": pass_, "db_name": dbname}


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Carga variables de entorno para la conexión a DB y JWT.
    """

    # Nombre de la aplicación
    app_name: str = "Akademus"
    app_version: str = "1.0.0"

    # PostgreSQL connection (Supabase production)
    # Try DATABASE_URL first, otherwise use individual params
    db_host: str = "db.czhvprbxvhqpprgaiqjd.supabase.co"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "1323Bri@ncisc0"
    db_name: str = "postgres"

    # JWT configuration
    # Secret key para firmar tokens JWT
    secret_key: str = "akademus-secret-key-change-in-production-2024"
    # Algoritmo HS256
    algorithm: str = "HS256"
    # Access token expira en 15 minutos
    access_token_expire_minutes: int = 15
    # Refresh token expira en 7 días
    refresh_token_expire_days: int = 7

    # OTP configuration
    # Código expira en 10 minutos
    otp_expire_minutes: int = 10
    # Máximo 3 intentos
    otp_max_attempts: int = 3

    # Twilio (simulado en desarrollo)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuración cacheada.
    Solo se carga una vez al iniciar la aplicación.
    """
    settings = Settings()
    
    # Override with DATABASE_URL if provided
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        parsed = parse_database_url(db_url)
        if parsed:
            settings.db_host = parsed["host"]
            settings.db_port = parsed["port"]
            settings.db_user = parsed["user"]
            settings.db_password = parsed["password"]
            settings.db_name = parsed["db_name"]
    
    return settings
