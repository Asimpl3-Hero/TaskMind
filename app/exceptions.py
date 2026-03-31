from fastapi import HTTPException, status


class TaskNotFoundError(HTTPException):
    def __init__(self, task_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con id {task_id} no encontrada",
        )


class ExternalServiceError(HTTPException):
    """Error al comunicarse con un servicio externo (OpenAI, etc.)."""

    def __init__(self, service: str, detail: str | None = None):
        message = f"Error al comunicarse con {service}"
        if detail:
            message += f": {detail}"
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=message,
        )


class AgentTimeoutError(HTTPException):
    def __init__(self, max_iterations: int):
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"El agente excedio el limite de {max_iterations} iteraciones",
        )
