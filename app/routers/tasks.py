from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.task import TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskFilters
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await task_service.create_task(db, data)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    status: TaskStatus | None = Query(None),
    priority: TaskPriority | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    filters = TaskFilters(
        status=status, priority=priority, date_from=date_from, date_to=date_to
    )
    return await task_service.get_tasks(db, filters)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    return await task_service.get_task(db, task_id)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int, data: TaskUpdate, db: AsyncSession = Depends(get_db)
):
    return await task_service.update_task(db, task_id, data)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    await task_service.delete_task(db, task_id)
