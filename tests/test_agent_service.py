import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus, TaskPriority
from app.services.agent_service import _serialize_task, execute_tool, _run_tool, chat
from app.agent import memory


class TestSerializeTask:
    def test_full_task(self):
        task = MagicMock(spec=Task)
        task.id = 1
        task.title = "Test"
        task.description = "Desc"
        task.status = TaskStatus.pending
        task.priority = TaskPriority.high
        task.due_date = datetime(2026, 6, 1)
        task.created_at = datetime(2026, 1, 1)
        task.updated_at = datetime(2026, 1, 1)

        result = _serialize_task(task)
        assert result["id"] == 1
        assert result["title"] == "Test"
        assert result["status"] == "pending"
        assert result["priority"] == "high"
        assert result["due_date"] == "2026-06-01T00:00:00"

    def test_null_due_date(self):
        task = MagicMock(spec=Task)
        task.id = 2
        task.title = "No date"
        task.description = None
        task.status = TaskStatus.completed
        task.priority = TaskPriority.low
        task.due_date = None
        task.created_at = datetime(2026, 1, 1)
        task.updated_at = datetime(2026, 1, 1)

        result = _serialize_task(task)
        assert result["due_date"] is None
        assert result["description"] is None


class TestExecuteTool:
    @pytest.mark.asyncio
    async def test_successful_execution(self, db_session: AsyncSession, sample_task: Task):
        result_str = await execute_tool("get_task", {"task_id": sample_task.id}, db_session)
        result = json.loads(result_str)
        assert result["id"] == sample_task.id

    @pytest.mark.asyncio
    async def test_error_handling(self, db_session: AsyncSession):
        result_str = await execute_tool("get_task", {"task_id": 9999}, db_session)
        result = json.loads(result_str)
        assert "error" in result


class TestRunTool:
    @pytest.mark.asyncio
    async def test_create_task(self, db_session: AsyncSession):
        result = await _run_tool("create_task", {"title": "Via tool"}, db_session)
        assert result["title"] == "Via tool"
        assert "id" in result

    @pytest.mark.asyncio
    async def test_list_tasks(self, db_session: AsyncSession, multiple_tasks):
        result = await _run_tool("list_tasks", {}, db_session)
        assert isinstance(result, list)
        assert len(result) == 4

    @pytest.mark.asyncio
    async def test_list_tasks_filtered(self, db_session: AsyncSession, multiple_tasks):
        result = await _run_tool("list_tasks", {"status": "pending"}, db_session)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_task(self, db_session: AsyncSession, sample_task: Task):
        result = await _run_tool("get_task", {"task_id": sample_task.id}, db_session)
        assert result["title"] == "Test task"

    @pytest.mark.asyncio
    async def test_update_task(self, db_session: AsyncSession, sample_task: Task):
        result = await _run_tool(
            "update_task", {"task_id": sample_task.id, "title": "Updated"}, db_session
        )
        assert result["title"] == "Updated"

    @pytest.mark.asyncio
    async def test_delete_task(self, db_session: AsyncSession, sample_task: Task):
        result = await _run_tool("delete_task", {"task_id": sample_task.id}, db_session)
        assert result["deleted"] is True

    @pytest.mark.asyncio
    async def test_bulk_update_status(self, db_session: AsyncSession, multiple_tasks):
        result = await _run_tool(
            "bulk_update_status",
            {"new_status": "completed", "status_filter": "pending"},
            db_session,
        )
        assert result["updated_count"] == 2

    @pytest.mark.asyncio
    async def test_bulk_delete(self, db_session: AsyncSession, multiple_tasks):
        result = await _run_tool(
            "bulk_delete", {"status_filter": "completed"}, db_session
        )
        assert result["deleted_count"] == 1

    @pytest.mark.asyncio
    async def test_count_tasks(self, db_session: AsyncSession, multiple_tasks):
        result = await _run_tool("count_tasks", {}, db_session)
        assert result["count"] == 4

    @pytest.mark.asyncio
    async def test_get_most_urgent(self, db_session: AsyncSession, multiple_tasks):
        result = await _run_tool("get_most_urgent", {}, db_session)
        assert "title" in result

    @pytest.mark.asyncio
    async def test_get_most_urgent_none(self, db_session: AsyncSession):
        result = await _run_tool("get_most_urgent", {}, db_session)
        assert "message" in result

    @pytest.mark.asyncio
    async def test_get_overdue_tasks(self, db_session: AsyncSession, multiple_tasks):
        result = await _run_tool("get_overdue_tasks", {}, db_session)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_unknown_tool(self, db_session: AsyncSession):
        result = await _run_tool("nonexistent", {}, db_session)
        assert "error" in result


class TestChat:
    def setup_method(self):
        memory.conversations.clear()

    @pytest.mark.asyncio
    async def test_chat_simple_response(self, db_session: AsyncSession):
        mock_message = MagicMock()
        mock_message.content = "Hola, soy TaskMind"
        mock_message.tool_calls = None

        mock_choice = MagicMock()
        mock_choice.finish_reason = "stop"
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch("app.services.agent_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            result = await chat("Hola", "test_session", db_session)

        assert result["response"] == "Hola, soy TaskMind"
        assert result["actions_taken"] == []

    @pytest.mark.asyncio
    async def test_chat_with_tool_call(self, db_session: AsyncSession):
        # First response: tool call
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "count_tasks"
        mock_tool_call.function.arguments = '{}'

        mock_message1 = MagicMock()
        mock_message1.content = None
        mock_message1.tool_calls = [mock_tool_call]
        mock_message1.model_dump.return_value = {
            "role": "assistant",
            "content": None,
            "tool_calls": [{"id": "call_123", "function": {"name": "count_tasks", "arguments": "{}"}}],
        }

        mock_choice1 = MagicMock()
        mock_choice1.finish_reason = "tool_calls"
        mock_choice1.message = mock_message1

        mock_response1 = MagicMock()
        mock_response1.choices = [mock_choice1]

        # Second response: final text
        mock_message2 = MagicMock()
        mock_message2.content = "Tienes 0 tareas."
        mock_message2.tool_calls = None

        mock_choice2 = MagicMock()
        mock_choice2.finish_reason = "stop"
        mock_choice2.message = mock_message2

        mock_response2 = MagicMock()
        mock_response2.choices = [mock_choice2]

        with patch("app.services.agent_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                side_effect=[mock_response1, mock_response2]
            )
            result = await chat("Cuantas tareas tengo?", "test_session", db_session)

        assert result["response"] == "Tienes 0 tareas."
        assert len(result["actions_taken"]) == 1
        assert result["actions_taken"][0]["tool"] == "count_tasks"
