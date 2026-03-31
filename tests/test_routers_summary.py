from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


class TestMonthlyCreatedEndpoint:
    @pytest.mark.asyncio
    async def test_monthly_created(self, client: AsyncClient):
        response = await client.get("/api/summary/monthly-created")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        for entry in data:
            assert "month" in entry
            assert "count" in entry


class TestSummaryTodayEndpoint:
    @pytest.mark.asyncio
    async def test_summary_today(self, client: AsyncClient, multiple_tasks):
        mock_message = MagicMock()
        mock_message.content = "Todo va bien, tienes 4 tareas."

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch("app.routers.summary.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            response = await client.get("/api/summary/today")

        assert response.status_code == 200
        data = response.json()
        assert "statistics" in data
        assert "analysis" in data
        assert data["analysis"] == "Todo va bien, tienes 4 tareas."
        stats = data["statistics"]
        assert stats["total_tasks"] == 4
        assert "by_status" in stats
        assert "by_priority" in stats

    @pytest.mark.asyncio
    async def test_summary_empty(self, client: AsyncClient):
        mock_message = MagicMock()
        mock_message.content = "No hay tareas."

        mock_choice = MagicMock()
        mock_choice.message = mock_message

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch("app.routers.summary.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            response = await client.get("/api/summary/today")

        assert response.status_code == 200
        assert response.json()["statistics"]["total_tasks"] == 0
