from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.agent import memory
from app.services import agent_service

router = APIRouter(prefix="/api/agent", tags=["agent"])


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    actions_taken: list


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    result = await agent_service.chat(request.message, request.session_id, db)
    return result


@router.delete("/history")
async def clear_history(session_id: str = "default"):
    memory.clear_history(session_id)
    return {"message": f"Historial de sesión '{session_id}' eliminado"}
