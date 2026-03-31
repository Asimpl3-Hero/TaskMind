from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.agent import memory


class TestChatEndpoint:
    def setup_method(self):
        memory.conversations.clear()

    @pytest.mark.asyncio
    async def test_chat(self, client: AsyncClient):
        mock_result = {
            "response": "Hola, soy TaskMind",
            "actions_taken": [],
        }
        with patch("app.services.agent_service.chat", new_callable=AsyncMock, return_value=mock_result):
            response = await client.post(
                "/api/agent/chat",
                json={"message": "Hola", "session_id": "test"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hola, soy TaskMind"
        assert data["actions_taken"] == []

    @pytest.mark.asyncio
    async def test_chat_empty_message(self, client: AsyncClient):
        response = await client.post(
            "/api/agent/chat",
            json={"message": "", "session_id": "test"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_default_session(self, client: AsyncClient):
        mock_result = {"response": "ok", "actions_taken": []}
        with patch("app.services.agent_service.chat", new_callable=AsyncMock, return_value=mock_result):
            response = await client.post(
                "/api/agent/chat", json={"message": "test"}
            )
        assert response.status_code == 200


class TestClearHistoryEndpoint:
    def setup_method(self):
        memory.conversations.clear()

    @pytest.mark.asyncio
    async def test_clear_history(self, client: AsyncClient):
        memory.add_message("test_sess", {"role": "user", "content": "hi"})
        response = await client.delete("/api/agent/history", params={"session_id": "test_sess"})
        assert response.status_code == 200
        assert "test_sess" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_clear_default_session(self, client: AsyncClient):
        response = await client.delete("/api/agent/history")
        assert response.status_code == 200
        assert "default" in response.json()["message"]
