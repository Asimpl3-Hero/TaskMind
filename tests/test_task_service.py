from datetime import datetime

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilters
from app.services import task_service


class TestCreateTask:
    @pytest.mark.asyncio
    async def test_create_minimal(self, db_session: AsyncSession):
        data = TaskCreate(title="New task")
        task = await task_service.create_task(db_session, data)
        assert task.id is not None
        assert task.title == "New task"
        assert task.status == TaskStatus.pending
        assert task.priority == TaskPriority.medium

    @pytest.mark.asyncio
    async def test_create_full(self, db_session: AsyncSession):
        data = TaskCreate(
            title="Full task",
            description="Details",
            status=TaskStatus.in_progress,
            priority=TaskPriority.high,
            due_date=datetime(2026, 6, 1),
        )
        task = await task_service.create_task(db_session, data)
        assert task.title == "Full task"
        assert task.description == "Details"
        assert task.status == TaskStatus.in_progress
        assert task.priority == TaskPriority.high
        assert task.due_date == datetime(2026, 6, 1)


class TestGetTasks:
    @pytest.mark.asyncio
    async def test_empty(self, db_session: AsyncSession):
        tasks = await task_service.get_tasks(db_session, TaskFilters())
        assert tasks == []

    @pytest.mark.asyncio
    async def test_returns_all(self, db_session: AsyncSession, multiple_tasks):
        tasks = await task_service.get_tasks(db_session, TaskFilters())
        assert len(tasks) == 4

    @pytest.mark.asyncio
    async def test_filter_by_status(self, db_session: AsyncSession, multiple_tasks):
        tasks = await task_service.get_tasks(
            db_session, TaskFilters(status=TaskStatus.pending)
        )
        assert all(t.status == TaskStatus.pending for t in tasks)
        assert len(tasks) == 2

    @pytest.mark.asyncio
    async def test_filter_by_priority(self, db_session: AsyncSession, multiple_tasks):
        tasks = await task_service.get_tasks(
            db_session, TaskFilters(priority=TaskPriority.high)
        )
        assert all(t.priority == TaskPriority.high for t in tasks)
        assert len(tasks) == 2

    @pytest.mark.asyncio
    async def test_filter_by_date_range(self, db_session: AsyncSession, multiple_tasks):
        tasks = await task_service.get_tasks(
            db_session,
            TaskFilters(
                date_from=datetime(2026, 4, 1),
                date_to=datetime(2026, 4, 15),
            ),
        )
        assert len(tasks) == 2  # Pending low (Apr 10) and In progress high (Apr 5)


class TestGetTask:
    @pytest.mark.asyncio
    async def test_found(self, db_session: AsyncSession, sample_task: Task):
        task = await task_service.get_task(db_session, sample_task.id)
        assert task.id == sample_task.id
        assert task.title == "Test task"

    @pytest.mark.asyncio
    async def test_not_found(self, db_session: AsyncSession):
        with pytest.raises(HTTPException) as exc_info:
            await task_service.get_task(db_session, 9999)
        assert exc_info.value.status_code == 404


class TestUpdateTask:
    @pytest.mark.asyncio
    async def test_update_title(self, db_session: AsyncSession, sample_task: Task):
        data = TaskUpdate(title="Updated title")
        updated = await task_service.update_task(db_session, sample_task.id, data)
        assert updated.title == "Updated title"
        assert updated.status == TaskStatus.pending  # unchanged

    @pytest.mark.asyncio
    async def test_update_status(self, db_session: AsyncSession, sample_task: Task):
        data = TaskUpdate(status=TaskStatus.completed)
        updated = await task_service.update_task(db_session, sample_task.id, data)
        assert updated.status == TaskStatus.completed

    @pytest.mark.asyncio
    async def test_update_not_found(self, db_session: AsyncSession):
        with pytest.raises(HTTPException) as exc_info:
            await task_service.update_task(db_session, 9999, TaskUpdate(title="x"))
        assert exc_info.value.status_code == 404


class TestDeleteTask:
    @pytest.mark.asyncio
    async def test_delete(self, db_session: AsyncSession, sample_task: Task):
        await task_service.delete_task(db_session, sample_task.id)
        with pytest.raises(HTTPException):
            await task_service.get_task(db_session, sample_task.id)

    @pytest.mark.asyncio
    async def test_delete_not_found(self, db_session: AsyncSession):
        with pytest.raises(HTTPException) as exc_info:
            await task_service.delete_task(db_session, 9999)
        assert exc_info.value.status_code == 404


class TestBulkUpdateStatus:
    @pytest.mark.asyncio
    async def test_bulk_update_all(self, db_session: AsyncSession, multiple_tasks):
        count = await task_service.bulk_update_status(db_session, TaskStatus.completed)
        assert count == 4

    @pytest.mark.asyncio
    async def test_bulk_update_by_status(self, db_session: AsyncSession, multiple_tasks):
        count = await task_service.bulk_update_status(
            db_session, TaskStatus.completed, status_filter=TaskStatus.pending
        )
        assert count == 2

    @pytest.mark.asyncio
    async def test_bulk_update_by_priority(self, db_session: AsyncSession, multiple_tasks):
        count = await task_service.bulk_update_status(
            db_session, TaskStatus.in_progress, priority_filter=TaskPriority.high
        )
        assert count == 2


class TestBulkDelete:
    @pytest.mark.asyncio
    async def test_bulk_delete_by_status(self, db_session: AsyncSession, multiple_tasks):
        count = await task_service.bulk_delete(db_session, status_filter=TaskStatus.completed)
        assert count == 1

    @pytest.mark.asyncio
    async def test_bulk_delete_all(self, db_session: AsyncSession, multiple_tasks):
        count = await task_service.bulk_delete(db_session)
        assert count == 4


class TestCountTasks:
    @pytest.mark.asyncio
    async def test_count_all(self, db_session: AsyncSession, multiple_tasks):
        count = await task_service.count_tasks(db_session, TaskFilters())
        assert count == 4

    @pytest.mark.asyncio
    async def test_count_filtered(self, db_session: AsyncSession, multiple_tasks):
        count = await task_service.count_tasks(
            db_session, TaskFilters(status=TaskStatus.pending)
        )
        assert count == 2

    @pytest.mark.asyncio
    async def test_count_empty(self, db_session: AsyncSession):
        count = await task_service.count_tasks(db_session, TaskFilters())
        assert count == 0


class TestGetMostUrgent:
    @pytest.mark.asyncio
    async def test_returns_soonest(self, db_session: AsyncSession, multiple_tasks):
        task = await task_service.get_most_urgent(db_session)
        assert task is not None
        # Overdue task has due_date 2020-01-01 which is soonest
        assert task.title == "Overdue task"

    @pytest.mark.asyncio
    async def test_returns_none_when_empty(self, db_session: AsyncSession):
        task = await task_service.get_most_urgent(db_session)
        assert task is None


class TestGetOverdueTasks:
    @pytest.mark.asyncio
    async def test_returns_overdue(self, db_session: AsyncSession, multiple_tasks):
        tasks = await task_service.get_overdue_tasks(db_session)
        assert len(tasks) >= 1
        assert all(t.status != TaskStatus.completed for t in tasks)

    @pytest.mark.asyncio
    async def test_empty_when_no_overdue(self, db_session: AsyncSession):
        tasks = await task_service.get_overdue_tasks(db_session)
        assert tasks == []


class TestGetTasksSummary:
    @pytest.mark.asyncio
    async def test_summary_structure(self, db_session: AsyncSession, multiple_tasks):
        summary = await task_service.get_tasks_summary(db_session)
        assert "total_tasks" in summary
        assert "by_status" in summary
        assert "by_priority" in summary
        assert "overdue" in summary
        assert "due_today" in summary
        assert "due_this_week" in summary

    @pytest.mark.asyncio
    async def test_summary_counts(self, db_session: AsyncSession, multiple_tasks):
        summary = await task_service.get_tasks_summary(db_session)
        assert summary["total_tasks"] == 4
        assert summary["by_status"]["pending"] == 2
        assert summary["by_status"]["in_progress"] == 1
        assert summary["by_status"]["completed"] == 1

    @pytest.mark.asyncio
    async def test_summary_empty(self, db_session: AsyncSession):
        summary = await task_service.get_tasks_summary(db_session)
        assert summary["total_tasks"] == 0


class TestGetMonthlyCreated:
    @pytest.mark.asyncio
    async def test_returns_5_months(self, db_session: AsyncSession):
        months = await task_service.get_monthly_created(db_session)
        assert len(months) == 5
        for m in months:
            assert "month" in m
            assert "count" in m
