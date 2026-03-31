import asyncio
import os
from datetime import datetime

# Set env vars before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake-key")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.models.task import Task, TaskStatus, TaskPriority
from app.main import app

# SQLite async in-memory for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_task(db_session: AsyncSession) -> Task:
    task = Task(
        title="Test task",
        description="A test task",
        status=TaskStatus.pending,
        priority=TaskPriority.medium,
        due_date=datetime(2026, 12, 31, 18, 0, 0),
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def multiple_tasks(db_session: AsyncSession) -> list[Task]:
    tasks_data = [
        Task(
            title="Pending low",
            status=TaskStatus.pending,
            priority=TaskPriority.low,
            due_date=datetime(2026, 4, 10),
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        ),
        Task(
            title="In progress high",
            status=TaskStatus.in_progress,
            priority=TaskPriority.high,
            due_date=datetime(2026, 4, 5),
            created_at=datetime(2026, 1, 2),
            updated_at=datetime(2026, 1, 2),
        ),
        Task(
            title="Completed medium",
            status=TaskStatus.completed,
            priority=TaskPriority.medium,
            created_at=datetime(2026, 1, 3),
            updated_at=datetime(2026, 1, 3),
        ),
        Task(
            title="Overdue task",
            status=TaskStatus.pending,
            priority=TaskPriority.high,
            due_date=datetime(2020, 1, 1),
            created_at=datetime(2026, 1, 4),
            updated_at=datetime(2026, 1, 4),
        ),
    ]
    for t in tasks_data:
        db_session.add(t)
    await db_session.commit()
    for t in tasks_data:
        await db_session.refresh(t)
    return tasks_data
