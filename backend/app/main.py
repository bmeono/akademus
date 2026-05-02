from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .core.config import get_settings
from .api.routes import auth, users, simulacros, flashcards, feynman, dashboard, admin, comunidad

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Iniciando {settings.app_name} v{settings.app_version}")

    # ── Verificar conexión a BD ──
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

    # ── Migraciones automáticas ──
    try:
        from psycopg2 import connect
        conn = connect(
            host=settings.db_host, port=settings.db_port,
            user=settings.db_user, password=settings.db_password,
            database=settings.db_name,
        )
        cur = conn.cursor()

        migraciones = [
            ("consultas_ia_disponibles",
             "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS consultas_ia_disponibles INT DEFAULT 10"),
            ("simulacros_disponibles",
             "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS simulacros_disponibles INT DEFAULT 0"),
            ("comunidad_consultas", """
                CREATE TABLE IF NOT EXISTS comunidad_consultas (
                    id SERIAL PRIMARY KEY,
                    usuario_id INT REFERENCES usuarios(id),
                    materia VARCHAR(100),
                    pregunta TEXT,
                    respuesta TEXT,
                    fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
            ("publicidad", """
                CREATE TABLE IF NOT EXISTS publicidad (
                    id SERIAL PRIMARY KEY,
                    imagen_url TEXT NOT NULL,
                    enlace_url TEXT,
                    descripcion VARCHAR(200),
                    orden INTEGER DEFAULT 0,
                    activa BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """),
        ]

        for nombre, sql in migraciones:
            try:
                cur.execute(sql)
                print(f"Migración OK: {nombre}")
            except Exception as e:
                print(f"Migración skip ({nombre}): {e}")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error en migraciones: {e}")

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
app.include_router(admin.publicidad_router)   # ← endpoint público /publicidad

@app.get("/")
async def root():
    return {"status": "ok", "version": settings.app_version}

@app.get("/health")
async def health():
    return {"status": "healthy"}
