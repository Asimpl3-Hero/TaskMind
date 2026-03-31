import json
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from openai import AsyncOpenAI, APIConnectionError, RateLimitError, APIStatusError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.exceptions import ExternalServiceError
from app.services import task_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/summary", tags=["Resumen"])

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class StatusBreakdown(BaseModel):
    pending: int = Field(..., description="Tareas pendientes")
    in_progress: int = Field(..., description="Tareas en progreso")
    completed: int = Field(..., description="Tareas completadas")


class PriorityBreakdown(BaseModel):
    low: int = Field(..., description="Prioridad baja")
    medium: int = Field(..., description="Prioridad media")
    high: int = Field(..., description="Prioridad alta")


class Statistics(BaseModel):
    """Estadisticas estructuradas del estado actual de las tareas."""
    total_tasks: int = Field(..., description="Numero total de tareas")
    by_status: StatusBreakdown = Field(..., description="Distribucion por estado")
    by_priority: PriorityBreakdown = Field(..., description="Distribucion por prioridad")
    overdue: int = Field(..., description="Tareas con fecha limite vencida y no completadas")
    due_today: int = Field(..., description="Tareas que vencen hoy")
    due_this_week: int = Field(..., description="Tareas que vencen esta semana")


class SummaryResponse(BaseModel):
    """Resumen del dia con estadisticas y analisis generado por IA."""
    statistics: Statistics = Field(..., description="Datos estructurados del estado de las tareas")
    analysis: str = Field(..., description="Diagnostico y sugerencias de priorizacion generados por el agente IA")


class MonthCount(BaseModel):
    """Tareas creadas en un mes especifico."""
    month: str = Field(..., description="Mes en formato YYYY-MM")
    count: int = Field(..., description="Cantidad de tareas creadas ese mes")


@router.get(
    "/monthly-created",
    response_model=list[MonthCount],
    summary="Tareas creadas por mes (rango de 5 meses)",
    description="Retorna la cantidad de tareas creadas en un rango de 5 meses: 2 anteriores, el actual y 2 siguientes.",
    responses={200: {"description": "Lista de 5 elementos con mes y cantidad"}},
)
async def monthly_created(db: AsyncSession = Depends(get_db)):
    return await task_service.get_monthly_created(db)


@router.get(
    "/today",
    response_model=SummaryResponse,
    summary="Resumen del dia",
    description=(
        "Retorna un resumen completo del estado actual de las tareas: "
        "estadisticas (total, por estado, por prioridad, vencidas, proximas a vencer) "
        "y un analisis en lenguaje natural generado por IA con diagnostico y sugerencias."
    ),
    responses={200: {"description": "Resumen con estadisticas y analisis IA"}},
)
async def summary_today(db: AsyncSession = Depends(get_db)):
    statistics = await task_service.get_tasks_summary(db)

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente de gestion de tareas. "
                        "Analiza las estadisticas del dia y genera un diagnostico breve y claro en espanol. "
                        "Incluye sugerencias de priorizacion para el dia."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Estas son las estadisticas actuales de mis tareas:\n{json.dumps(statistics, ensure_ascii=False)}",
                },
            ],
        )
    except APIConnectionError:
        logger.error("No se pudo conectar con OpenAI para el resumen del dia")
        raise ExternalServiceError("OpenAI", "no se pudo establecer conexion")
    except RateLimitError:
        logger.warning("Rate limit alcanzado en OpenAI para el resumen del dia")
        raise ExternalServiceError("OpenAI", "limite de solicitudes excedido, intente mas tarde")
    except APIStatusError as e:
        logger.error("Error de API OpenAI (status %s): %s", e.status_code, e.message)
        raise ExternalServiceError("OpenAI", f"error del servicio (status {e.status_code})")

    analysis = response.choices[0].message.content

    return {"statistics": statistics, "analysis": analysis}
