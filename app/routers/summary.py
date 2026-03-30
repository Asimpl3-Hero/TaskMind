import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.services import task_service

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

    analysis = response.choices[0].message.content

    return {"statistics": statistics, "analysis": analysis}
