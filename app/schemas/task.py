from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    """Schema para crear una nueva tarea."""
    title: str = Field(..., min_length=1, max_length=255, description="Titulo de la tarea", examples=["Revisar propuesta"])
    description: str | None = Field(None, description="Descripcion detallada de la tarea", examples=["Revisar el documento del cliente antes del viernes"])
    status: TaskStatus = Field(TaskStatus.pending, description="Estado inicial de la tarea")
    priority: TaskPriority = Field(TaskPriority.medium, description="Nivel de prioridad")
    due_date: datetime | None = Field(None, description="Fecha limite en formato ISO 8601", examples=["2026-04-04T18:00:00"])


class TaskUpdate(BaseModel):
    """Schema para actualizar una tarea existente. Solo se actualizan los campos enviados."""
    title: str | None = Field(None, min_length=1, max_length=255, description="Nuevo titulo")
    description: str | None = Field(None, description="Nueva descripcion")
    status: TaskStatus | None = Field(None, description="Nuevo estado")
    priority: TaskPriority | None = Field(None, description="Nueva prioridad")
    due_date: datetime | None = Field(None, description="Nueva fecha limite")


class TaskResponse(BaseModel):
    """Representacion completa de una tarea en las respuestas de la API."""
    id: int = Field(..., description="Identificador unico de la tarea")
    title: str = Field(..., description="Titulo de la tarea")
    description: str | None = Field(None, description="Descripcion de la tarea")
    status: TaskStatus = Field(..., description="Estado actual")
    priority: TaskPriority = Field(..., description="Nivel de prioridad")
    due_date: datetime | None = Field(None, description="Fecha limite")
    created_at: datetime = Field(..., description="Fecha de creacion")
    updated_at: datetime = Field(..., description="Fecha de ultima actualizacion")

    model_config = ConfigDict(from_attributes=True)


class TaskFilters(BaseModel):
    """Filtros opcionales para consultar tareas."""
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
