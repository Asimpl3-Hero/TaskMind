from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.task import TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskFilters
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["Tareas"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=201,
    summary="Crear tarea",
    description="Crea una nueva tarea. El titulo es obligatorio; estado, prioridad y fecha limite son opcionales con valores por defecto.",
    responses={201: {"description": "Tarea creada exitosamente"}},
)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await task_service.create_task(db, data)


@router.get(
    "",
    response_model=list[TaskResponse],
    summary="Listar tareas",
    description="Retorna todas las tareas. Soporta filtros opcionales por estado, prioridad y rango de fechas (date_from, date_to en ISO 8601).",
    responses={200: {"description": "Lista de tareas"}},
)
async def list_tasks(
    status: TaskStatus | None = Query(None, description="Filtrar por estado"),
    priority: TaskPriority | None = Query(None, description="Filtrar por prioridad"),
    date_from: datetime | None = Query(None, description="Fecha limite desde (ISO 8601)"),
    date_to: datetime | None = Query(None, description="Fecha limite hasta (ISO 8601)"),
    db: AsyncSession = Depends(get_db),
):
    filters = TaskFilters(
        status=status, priority=priority, date_from=date_from, date_to=date_to
    )
    return await task_service.get_tasks(db, filters)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Obtener tarea",
    description="Retorna el detalle completo de una tarea por su ID.",
    responses={
        200: {"description": "Detalle de la tarea"},
        404: {"description": "Tarea no encontrada"},
    },
)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    return await task_service.get_task(db, task_id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Actualizar tarea",
    description="Actualiza los campos enviados de una tarea existente. Solo se modifican los campos incluidos en el body.",
    responses={
        200: {"description": "Tarea actualizada"},
        404: {"description": "Tarea no encontrada"},
    },
)
async def update_task(
    task_id: int, data: TaskUpdate, db: AsyncSession = Depends(get_db)
):
    return await task_service.update_task(db, task_id, data)


@router.delete(
    "/{task_id}",
    status_code=204,
    summary="Eliminar tarea",
    description="Elimina permanentemente una tarea por su ID.",
    responses={
        204: {"description": "Tarea eliminada"},
        404: {"description": "Tarea no encontrada"},
    },
)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    await task_service.delete_task(db, task_id)
