import os
import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000")
TIMEOUT = 30


def _client() -> httpx.Client:
    return httpx.Client(base_url=API_URL, timeout=TIMEOUT)


# --- Tasks ---

def create_task(payload: dict) -> httpx.Response:
    with _client() as c:
        return c.post("/api/tasks", json=payload)


def get_tasks(params: dict | None = None) -> list:
    with _client() as c:
        r = c.get("/api/tasks", params=params or {})
    return r.json() if r.status_code == 200 else []


def update_task(task_id: int, payload: dict) -> httpx.Response:
    with _client() as c:
        return c.put(f"/api/tasks/{task_id}", json=payload)


def delete_task(task_id: int) -> httpx.Response:
    with _client() as c:
        return c.delete(f"/api/tasks/{task_id}")


# --- Agent ---

def agent_chat(message: str, session_id: str = "default") -> dict | None:
    with _client() as c:
        r = c.post("/api/agent/chat", json={"message": message, "session_id": session_id})
    return r.json() if r.status_code == 200 else None


def agent_clear_history(session_id: str = "default") -> None:
    with _client() as c:
        c.delete("/api/agent/history", params={"session_id": session_id})


# --- Summary ---

def get_summary() -> dict | None:
    with _client() as c:
        r = c.get("/api/summary/today")
    return r.json() if r.status_code == 200 else None


def get_weekly_completed() -> list:
    with _client() as c:
        r = c.get("/api/summary/weekly-completed")
    return r.json() if r.status_code == 200 else []
