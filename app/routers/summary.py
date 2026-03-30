import json

from fastapi import APIRouter, Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.services import task_service

router = APIRouter(prefix="/api/summary", tags=["summary"])

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


@router.get("/today")
async def summary_today(db: AsyncSession = Depends(get_db)):
    statistics = await task_service.get_tasks_summary(db)

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un asistente de gestión de tareas. "
                    "Analiza las estadísticas del día y genera un diagnóstico breve y claro en español. "
                    "Incluye sugerencias de priorización para el día."
                ),
            },
            {
                "role": "user",
                "content": f"Estas son las estadísticas actuales de mis tareas:\n{json.dumps(statistics, ensure_ascii=False)}",
            },
        ],
    )

    analysis = response.choices[0].message.content

    return {"statistics": statistics, "analysis": analysis}
