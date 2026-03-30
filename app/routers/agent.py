from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.agent import memory
from app.services import agent_service

router = APIRouter(prefix="/api/agent", tags=["Agente IA"])


class ChatRequest(BaseModel):
    """Mensaje del usuario para el agente IA."""
    message: str = Field(
        ...,
        min_length=1,
        description="Instruccion en lenguaje natural",
        examples=["Crea una tarea llamada 'Revisar propuesta' con prioridad alta para el viernes"],
    )
    session_id: str = Field("default", description="Identificador de sesion para mantener contexto de conversacion")


class ActionDetail(BaseModel):
    """Detalle de una accion ejecutada por el agente."""
    tool: str = Field(..., description="Nombre de la herramienta ejecutada", examples=["create_task"])
    arguments: dict = Field(..., description="Argumentos enviados a la herramienta")
    result: dict | list = Field(..., description="Resultado de la ejecucion")


class ChatResponse(BaseModel):
    """Respuesta del agente IA con el mensaje y las acciones realizadas."""
    response: str = Field(..., description="Respuesta del agente en lenguaje natural")
    actions_taken: list[ActionDetail] = Field(default_factory=list, description="Lista de acciones ejecutadas sobre las tareas")


class MessageResponse(BaseModel):
    """Respuesta generica con mensaje de confirmacion."""
    message: str


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Enviar mensaje al agente",
    description=(
        "Envia una instruccion en lenguaje natural al agente IA. "
        "El agente interpreta el mensaje, ejecuta las acciones necesarias sobre las tareas "
        "y retorna una respuesta con el resultado. "
        "El historial de conversacion se mantiene por session_id."
    ),
    responses={200: {"description": "Respuesta del agente con acciones ejecutadas"}},
)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    result = await agent_service.chat(request.message, request.session_id, db)
    return result


@router.delete(
    "/history",
    response_model=MessageResponse,
    summary="Limpiar historial",
    description="Elimina el historial de conversacion de una sesion. El agente pierde el contexto previo.",
    responses={200: {"description": "Historial eliminado"}},
)
async def clear_history(
    session_id: str = Query("default", description="ID de la sesion a limpiar"),
):
    memory.clear_history(session_id)
    return {"message": f"Historial de sesion '{session_id}' eliminado"}
