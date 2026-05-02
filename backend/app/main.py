from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .core.config import get_settings
from .api.routes import auth, users, simulacros, flashcards, feynman, dashboard, admin, comunidad

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Iniciando {settings.app_name} v{settings.app_version}")
    try:
        from psycopg2 import connect
        conn = connect(
            host=settings.db_host, port=settings.db_port,
            user=settings.db_user, password=settings.db_password,
            database=settings.db_name,
        )
        conn.close()
        print(f"Conexión a PostgreSQL: OK (host={settings.db_host}, port={settings.db_port})")
    except Exception as e:
        print(f"Conexión a PostgreSQL: ERROR - {e}")

    try:
        from psycopg2 import connect
        conn = connect(
            host=settings.db_host, port=settings.db_port,
            user=settings.db_user, password=settings.db_password,
            database=settings.db_name,
        )
        cur = conn.cursor()
        try:
            cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS consultas_ia_disponibles INT DEFAULT 10")
            print("Columna consultas_ia_disponibles creada")
        except: pass
        try:
            cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS simulacros_disponibles INT DEFAULT 0")
            print("Columna simulacros_disponibles creada")
        except: pass
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS comunidad_consultas (
                    id SERIAL PRIMARY KEY,
                    usuario_id INT REFERENCES usuarios(id),
                    materia VARCHAR(100),
                    pregunta TEXT,
                    respuesta TEXT,
                    fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Tabla comunidad_consultas creada")
        except: pass
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Migracion error: {e}")

    yield

    from app.core.db import close_pool
    close_pool()
    print("Cerrando aplicación - pool de conexiones cerrado")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Simulador de exámenes de admisión",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://akademus.online",
        "https://www.akademus.online",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(simulacros.router)
app.include_router(flashcards.router)
app.include_router(feynman.router)
app.include_router(feynman.admin_router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(comunidad.router)

@app.get("/")
async def root():
    return {"status": "ok", "version": settings.app_version}

@app.get("/health")
async def health():
    return {"status": "healthy"}
