from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import get_settings
from .api.routes import auth, users, simulacros, flashcards, feynman, dashboard, admin


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager.
    Se ejecuta al iniciar y cerrar la aplicación.
    """
    print(f"Iniciando {settings.app_name} v{settings.app_version}")
    # Verify DB connection
    try:
        from psycopg2 import connect
        conn = connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
        )
        conn.close()
        print(f"Conexión a PostgreSQL: OK (host={settings.db_host}, port={settings.db_port})")
    except Exception as e:
        print(f"Conexión a PostgreSQL: ERROR - {e}")
    yield
    print("Cerrando aplicación")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Simulador de exámenes de admisión",
    lifespan=lifespan,
)

# CORS - allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(simulacros.router)
app.include_router(flashcards.router)
app.include_router(feynman.router)
app.include_router(feynman.admin_router)
app.include_router(dashboard.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "online",
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}
