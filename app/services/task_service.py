from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilters


async def create_task(db: AsyncSession, data: TaskCreate) -> Task:
    task = Task(**data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks(db: AsyncSession, filters: TaskFilters) -> list[Task]:
    query = select(Task)
    if filters.status:
        query = query.where(Task.status == filters.status)
    if filters.priority:
        query = query.where(Task.priority == filters.priority)
    if filters.date_from:
        query = query.where(Task.due_date >= filters.date_from)
    if filters.date_to:
        query = query.where(Task.due_date <= filters.date_to)
    query = query.order_by(Task.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_task(db: AsyncSession, task_id: int) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task


async def update_task(db: AsyncSession, task_id: int, data: TaskUpdate) -> Task:
    task = await get_task(db, task_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int) -> None:
    task = await get_task(db, task_id)
    await db.delete(task)
    await db.commit()


async def get_tasks_summary(db: AsyncSession) -> dict:
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    week_end = today_start + timedelta(days=7)

    total = await db.scalar(select(func.count(Task.id)))

    by_status = {}
    for s in TaskStatus:
        count = await db.scalar(
            select(func.count(Task.id)).where(Task.status == s)
        )
        by_status[s.value] = count or 0

    by_priority = {}
    for p in TaskPriority:
        count = await db.scalar(
            select(func.count(Task.id)).where(Task.priority == p)
        )
        by_priority[p.value] = count or 0

    overdue = await db.scalar(
        select(func.count(Task.id)).where(
            Task.due_date < now,
            Task.status != TaskStatus.completed,
        )
    )

    due_today = await db.scalar(
        select(func.count(Task.id)).where(
            Task.due_date >= today_start,
            Task.due_date < today_end,
            Task.status != TaskStatus.completed,
        )
    )

    due_this_week = await db.scalar(
        select(func.count(Task.id)).where(
            Task.due_date >= today_start,
            Task.due_date < week_end,
            Task.status != TaskStatus.completed,
        )
    )

    return {
        "total_tasks": total or 0,
        "by_status": by_status,
        "by_priority": by_priority,
        "overdue": overdue or 0,
        "due_today": due_today or 0,
        "due_this_week": due_this_week or 0,
    }
