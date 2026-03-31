import pytest
from httpx import AsyncClient

from app.models.task import Task


class TestCreateTaskEndpoint:
    @pytest.mark.asyncio
    async def test_create_task(self, client: AsyncClient):
        response = await client.post("/api/tasks", json={"title": "New task"})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New task"
        assert data["status"] == "pending"
        assert data["priority"] == "medium"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_full_task(self, client: AsyncClient):
        response = await client.post(
            "/api/tasks",
            json={
                "title": "Full",
                "description": "Desc",
                "status": "in_progress",
                "priority": "high",
                "due_date": "2026-06-01T18:00:00",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["priority"] == "high"

    @pytest.mark.asyncio
    async def test_create_empty_title(self, client: AsyncClient):
        response = await client.post("/api/tasks", json={"title": ""})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_missing_title(self, client: AsyncClient):
        response = await client.post("/api/tasks", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_invalid_status(self, client: AsyncClient):
        response = await client.post("/api/tasks", json={"title": "x", "status": "bad"})
        assert response.status_code == 422


class TestListTasksEndpoint:
    @pytest.mark.asyncio
    async def test_list_empty(self, client: AsyncClient):
        response = await client.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_tasks(self, client: AsyncClient, multiple_tasks):
        response = await client.get("/api/tasks")
        assert response.status_code == 200
        assert len(response.json()) == 4

    @pytest.mark.asyncio
    async def test_filter_by_status(self, client: AsyncClient, multiple_tasks):
        response = await client.get("/api/tasks", params={"status": "pending"})
        assert response.status_code == 200
        data = response.json()
        assert all(t["status"] == "pending" for t in data)

    @pytest.mark.asyncio
    async def test_filter_by_priority(self, client: AsyncClient, multiple_tasks):
        response = await client.get("/api/tasks", params={"priority": "high"})
        assert response.status_code == 200
        data = response.json()
        assert all(t["priority"] == "high" for t in data)

    @pytest.mark.asyncio
    async def test_filter_by_date_range(self, client: AsyncClient, multiple_tasks):
        response = await client.get(
            "/api/tasks",
            params={"date_from": "2026-04-01T00:00:00", "date_to": "2026-04-15T00:00:00"},
        )
        assert response.status_code == 200


class TestGetTaskEndpoint:
    @pytest.mark.asyncio
    async def test_get_task(self, client: AsyncClient, sample_task: Task):
        response = await client.get(f"/api/tasks/{sample_task.id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Test task"

    @pytest.mark.asyncio
    async def test_get_not_found(self, client: AsyncClient):
        response = await client.get("/api/tasks/9999")
        assert response.status_code == 404


class TestUpdateTaskEndpoint:
    @pytest.mark.asyncio
    async def test_update_task(self, client: AsyncClient, sample_task: Task):
        response = await client.put(
            f"/api/tasks/{sample_task.id}", json={"title": "Updated"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    @pytest.mark.asyncio
    async def test_update_status(self, client: AsyncClient, sample_task: Task):
        response = await client.put(
            f"/api/tasks/{sample_task.id}", json={"status": "completed"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    @pytest.mark.asyncio
    async def test_update_not_found(self, client: AsyncClient):
        response = await client.put("/api/tasks/9999", json={"title": "x"})
        assert response.status_code == 404


class TestDeleteTaskEndpoint:
    @pytest.mark.asyncio
    async def test_delete_task(self, client: AsyncClient, sample_task: Task):
        response = await client.delete(f"/api/tasks/{sample_task.id}")
        assert response.status_code == 204

        # Verify deleted
        response = await client.get(f"/api/tasks/{sample_task.id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_not_found(self, client: AsyncClient):
        response = await client.delete("/api/tasks/9999")
        assert response.status_code == 404
