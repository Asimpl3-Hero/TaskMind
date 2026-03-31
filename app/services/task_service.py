from datetime import datetime, timedelta

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import TaskNotFoundError
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
        raise TaskNotFoundError(task_id)
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


async def bulk_update_status(
    db: AsyncSession,
    new_status: TaskStatus,
    status_filter: TaskStatus | None = None,
    priority_filter: TaskPriority | None = None,
) -> int:
    query = update(Task).values(status=new_status)
    if status_filter:
        query = query.where(Task.status == status_filter)
    if priority_filter:
        query = query.where(Task.priority == priority_filter)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount


async def bulk_delete(
    db: AsyncSession,
    status_filter: TaskStatus | None = None,
    priority_filter: TaskPriority | None = None,
) -> int:
    query = delete(Task)
    if status_filter:
        query = query.where(Task.status == status_filter)
    if priority_filter:
        query = query.where(Task.priority == priority_filter)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount


async def count_tasks(db: AsyncSession, filters: TaskFilters) -> int:
    query = select(func.count(Task.id))
    if filters.status:
        query = query.where(Task.status == filters.status)
    if filters.priority:
        query = query.where(Task.priority == filters.priority)
    if filters.date_from:
        query = query.where(Task.due_date >= filters.date_from)
    if filters.date_to:
        query = query.where(Task.due_date <= filters.date_to)
    return await db.scalar(query) or 0


async def get_most_urgent(db: AsyncSession) -> Task | None:
    result = await db.execute(
        select(Task)
        .where(Task.due_date.isnot(None), Task.status != TaskStatus.completed)
        .order_by(Task.due_date.asc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_overdue_tasks(db: AsyncSession) -> list[Task]:
    now = datetime.utcnow()
    result = await db.execute(
        select(Task)
        .where(Task.due_date < now, Task.status != TaskStatus.completed)
        .order_by(Task.due_date.asc())
    )
    return list(result.scalars().all())


async def get_monthly_created(db: AsyncSession) -> list[dict]:
    now = datetime.utcnow()

    months = []
    for offset in range(-2, 3):
        year = now.year
        month = now.month + offset
        while month <= 0:
            month += 12
            year -= 1
        while month > 12:
            month -= 12
            year += 1
        months.append(datetime(year, month, 1))

    result = await db.execute(
        select(
            func.extract("year", Task.created_at).label("year"),
            func.extract("month", Task.created_at).label("month"),
            func.count(Task.id).label("count"),
        )
        .where(
            Task.created_at >= months[0],
            Task.created_at < months[-1] + timedelta(days=31),
        )
        .group_by(
            func.extract("year", Task.created_at),
            func.extract("month", Task.created_at),
        )
    )

    rows = {(int(r.year), int(r.month)): r.count for r in result.all()}

    return [
        {
            "month": m.strftime("%Y-%m"),
            "count": rows.get((m.year, m.month), 0),
        }
        for m in months
    ]


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
