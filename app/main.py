import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import engine
from app.routers import tasks, agent, summary

logger = logging.getLogger(__name__)

DESCRIPTION = """
## TaskMind API

Sistema de gestion de tareas con agente de inteligencia artificial.

### Funcionalidades

* **Tareas** - CRUD completo con filtros por estado, prioridad y rango de fechas.
* **Agente IA** - Interpreta instrucciones en lenguaje natural y ejecuta acciones sobre las tareas.
* **Resumen del dia** - Estadisticas y analisis generado por IA con sugerencias de priorizacion.

### Tecnologias

FastAPI + PostgreSQL + SQLAlchemy (async) + Alembic + OpenAI API
"""

TAGS_METADATA = [
    {
        "name": "Tareas",
        "description": "Operaciones CRUD sobre tareas. Soporta filtros por estado, prioridad y rango de fechas.",
    },
    {
        "name": "Agente IA",
        "description": "Interaccion con el agente de inteligencia artificial. Interpreta lenguaje natural y ejecuta acciones.",
    },
    {
        "name": "Resumen",
        "description": "Resumen diario con estadisticas estructuradas y analisis generado por IA.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="TaskMind API",
    description=DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error("Database error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "Error de conexion con la base de datos. Intente nuevamente."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled error on %s %s: %s", request.method, request.url.path, exc, exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor."},
    )


app.include_router(tasks.router)
app.include_router(agent.router)
app.include_router(summary.router)


@app.get("/", tags=["Health"], summary="Health check", description="Verifica que la API esta activa.")
async def root():
    return {"message": "TaskMind API is running"}
