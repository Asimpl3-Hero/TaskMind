TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Crear una nueva tarea",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Título de la tarea"},
                    "description": {"type": "string", "description": "Descripción de la tarea"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Prioridad: low, medium o high",
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Fecha límite en formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Listar tareas con filtros opcionales",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Filtrar por estado",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Filtrar por prioridad",
                    },
                    "date_from": {
                        "type": "string",
                        "description": "Fecha desde (ISO 8601)",
                    },
                    "date_to": {
                        "type": "string",
                        "description": "Fecha hasta (ISO 8601)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_task",
            "description": "Obtener el detalle de una tarea por su ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID de la tarea"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Actualizar campos de una tarea existente",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID de la tarea a actualizar"},
                    "title": {"type": "string", "description": "Nuevo título"},
                    "description": {"type": "string", "description": "Nueva descripción"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Nuevo estado",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Nueva prioridad",
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Nueva fecha límite (ISO 8601)",
                    },
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Eliminar una tarea por su ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID de la tarea a eliminar"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bulk_update_status",
            "description": "Cambiar el estado de múltiples tareas filtradas por estado y/o prioridad actual",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Nuevo estado a asignar",
                    },
                    "status_filter": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Filtrar tareas por estado actual",
                    },
                    "priority_filter": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Filtrar tareas por prioridad",
                    },
                },
                "required": ["new_status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bulk_delete",
            "description": "Eliminar múltiples tareas filtradas por estado y/o prioridad",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Filtrar tareas por estado",
                    },
                    "priority_filter": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Filtrar tareas por prioridad",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_tasks",
            "description": "Contar tareas con filtros opcionales",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "Filtrar por estado",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Filtrar por prioridad",
                    },
                    "date_from": {
                        "type": "string",
                        "description": "Fecha desde (ISO 8601)",
                    },
                    "date_to": {
                        "type": "string",
                        "description": "Fecha hasta (ISO 8601)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_most_urgent",
            "description": "Obtener la tarea más urgente (próxima a vencer y no completada)",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_overdue_tasks",
            "description": "Obtener todas las tareas vencidas (fecha límite pasada y no completadas)",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]
