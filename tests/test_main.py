import pytest
from httpx import AsyncClient

from app.main import app, TAGS_METADATA


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_root(self, client: AsyncClient):
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "TaskMind API is running"}


class TestAppConfig:
    def test_title(self):
        assert app.title == "TaskMind API"

    def test_version(self):
        assert app.version == "1.0.0"

    def test_docs_url(self):
        assert app.docs_url == "/docs"

    def test_redoc_url(self):
        assert app.redoc_url == "/redoc"

    def test_tags_metadata(self):
        assert len(TAGS_METADATA) == 3
        names = [t["name"] for t in TAGS_METADATA]
        assert "Tareas" in names
        assert "Agente IA" in names
        assert "Resumen" in names

    def test_routers_included(self):
        paths = [route.path for route in app.routes]
        assert "/api/tasks" in paths or any("/api/tasks" in p for p in paths)


class TestOpenAPI:
    @pytest.mark.asyncio
    async def test_openapi_schema(self, client: AsyncClient):
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "TaskMind API"
        assert "/api/tasks" in schema["paths"]
