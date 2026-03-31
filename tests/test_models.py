from datetime import datetime

from app.models.task import Task, TaskStatus, TaskPriority


class TestTaskStatus:
    def test_values(self):
        assert TaskStatus.pending.value == "pending"
        assert TaskStatus.in_progress.value == "in_progress"
        assert TaskStatus.completed.value == "completed"

    def test_is_str_enum(self):
        assert isinstance(TaskStatus.pending, str)
        assert TaskStatus.pending == "pending"

    def test_all_members(self):
        assert len(TaskStatus) == 3


class TestTaskPriority:
    def test_values(self):
        assert TaskPriority.low.value == "low"
        assert TaskPriority.medium.value == "medium"
        assert TaskPriority.high.value == "high"

    def test_is_str_enum(self):
        assert isinstance(TaskPriority.low, str)

    def test_all_members(self):
        assert len(TaskPriority) == 3


class TestTaskModel:
    def test_tablename(self):
        assert Task.__tablename__ == "tasks"

    def test_create_instance(self):
        task = Task(
            title="Test",
            description="Desc",
            status=TaskStatus.pending,
            priority=TaskPriority.high,
        )
        assert task.title == "Test"
        assert task.description == "Desc"
        assert task.status == TaskStatus.pending
        assert task.priority == TaskPriority.high

    def test_defaults(self):
        task = Task(title="Minimal")
        assert task.due_date is None
        assert task.description is None

    def test_columns_exist(self):
        columns = {c.name for c in Task.__table__.columns}
        expected = {"id", "title", "description", "status", "priority", "due_date", "created_at", "updated_at"}
        assert expected == columns
