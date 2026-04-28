import os
from pydantic_settings import BaseSettings
from functools import lru_cache


def parse_database_url(url: str = None):
    """Parse DATABASE_URL to extract connection parameters."""
    if not url or len(url.strip()) == 0:
        return None
    # Skip if doesn't start with postgres
    if not url.startswith("postgres"):
        return None
    # Remove query params
    url = url.split("?")[0]
    # postgres://user:pass@host:port/dbname
    parts = url.replace("postgres://", "").split("@")
    if len(parts) != 2:
        return None
    auth, host_db = parts
    # Handle case where password contains : 
    if ":" in auth:
        user_pass = auth.split(":")
        if len(user_pass) >= 2:
            user = user_pass[0]
            pass_ = ":".join(user_pass[1:])
    else:
        user = auth
        pass_ = ""
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
    """Configuración de la aplicación."""
    app_name: str = "Akademus"
    app_version: str = "1.0.0"

    # Neon DB (production)
    db_host: str = "ep-crimson-butterfly-amltr5by.c-5.us-east-1.aws.neon.tech"
    db_port: int = 5432
    db_user: str = "neondb_owner"
    db_password: str = "npg_uIUNP0ZR4bzO"
    db_name: str = "neondb"
    db_sslmode: str = "require"

    secret_key: str = "akademus-secret-key-change-in-production-2024"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    otp_expire_minutes: int = 10
    otp_max_attempts: int = 3
    twilio_account_sid: str = ""
    twilio_phone_number: str = "" 
    
    # Google OAuth - configurar en variables de entorno GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración cacheada."""
    return Settings()
