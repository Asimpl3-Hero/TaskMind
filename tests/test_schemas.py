from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskFilters
from app.models.task import TaskStatus, TaskPriority


class TestTaskCreate:
    def test_valid_minimal(self):
        t = TaskCreate(title="Do something")
        assert t.title == "Do something"
        assert t.status == TaskStatus.pending
        assert t.priority == TaskPriority.medium
        assert t.description is None
        assert t.due_date is None

    def test_valid_full(self):
        t = TaskCreate(
            title="Full task",
            description="Details",
            status=TaskStatus.in_progress,
            priority=TaskPriority.high,
            due_date=datetime(2026, 6, 1),
        )
        assert t.title == "Full task"
        assert t.status == TaskStatus.in_progress

    def test_empty_title_fails(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="")

    def test_title_too_long_fails(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="x" * 256)

    def test_invalid_status_fails(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="ok", status="invalid")

    def test_invalid_priority_fails(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="ok", priority="ultra")


class TestTaskUpdate:
    def test_all_none(self):
        t = TaskUpdate()
        assert t.title is None
        assert t.description is None
        assert t.status is None
        assert t.priority is None
        assert t.due_date is None

    def test_partial(self):
        t = TaskUpdate(title="New title", status=TaskStatus.completed)
        assert t.title == "New title"
        assert t.status == TaskStatus.completed
        assert t.priority is None

    def test_exclude_unset(self):
        t = TaskUpdate(title="Only title")
        dumped = t.model_dump(exclude_unset=True)
        assert dumped == {"title": "Only title"}

    def test_empty_title_fails(self):
        with pytest.raises(ValidationError):
            TaskUpdate(title="")


class TestTaskResponse:
    def test_from_attributes(self):
        data = {
            "id": 1,
            "title": "Test",
            "description": None,
            "status": TaskStatus.pending,
            "priority": TaskPriority.medium,
            "due_date": None,
            "created_at": datetime(2026, 1, 1),
            "updated_at": datetime(2026, 1, 1),
        }
        t = TaskResponse(**data)
        assert t.id == 1
        assert t.title == "Test"

    def test_missing_required_fails(self):
        with pytest.raises(ValidationError):
            TaskResponse(title="No id")


class TestTaskFilters:
    def test_all_none(self):
        f = TaskFilters()
        assert f.status is None
        assert f.priority is None
        assert f.date_from is None
        assert f.date_to is None

    def test_with_values(self):
        f = TaskFilters(status=TaskStatus.pending, priority=TaskPriority.high)
        assert f.status == TaskStatus.pending
        assert f.priority == TaskPriority.high
