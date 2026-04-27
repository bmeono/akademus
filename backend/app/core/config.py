from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Carga variables de entorno para la conexión a DB y JWT.
    """

    # Nombre de la aplicación
    app_name: str = "Akademus"
    app_version: str = "1.0.0"

    # PostgreSQL connection
    # Host: localhost (servidor PostgreSQL)
    # User: postgres
    # Password: 1323Bri@ncisc0
    # DB: akademus
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "1323Bri@ncisc0"
    db_name: str = "akademus"

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
    return Settings()
