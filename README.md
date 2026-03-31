# 🧠 TaskMind

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-Async-D71F00?style=flat&logo=sqlalchemy&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=flat&logo=openai&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-6BA81E?style=flat)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat&logo=pydantic&logoColor=white)

Sistema de gestion de tareas con agente de inteligencia artificial. Combina una API REST con un agente capaz de interpretar instrucciones en lenguaje natural y ejecutar acciones reales sobre los datos.

---

## 📋 Tabla de contenido

- [⚙️ Stack](#️-stack)
- [🗃️ Modelo de datos](#️-modelo-de-datos)
- [🔌 Endpoints](#-endpoints)
- [🤖 Agente IA](#-agente-ia)
- [📊 Resumen del dia](#-resumen-del-dia)
- [🖥️ Frontend](#️-frontend)
- [📄 Documentacion](#-documentacion)
- [🚀 Instalacion y ejecucion](#-instalacion-y-ejecucion)
- [📁 Estructura del proyecto](#-estructura-del-proyecto)
- [🧪 Tests](#-tests)
- [🧩 Decisiones tecnicas](#-decisiones-tecnicas)

---

## ⚙️ Stack

| Capa | Tecnologia |
|------|------------|
| 🌐 Backend | FastAPI |
| 🗄️ Base de datos | PostgreSQL 16 |
| 🔗 ORM | SQLAlchemy (async) + asyncpg |
| 📦 Migraciones | Alembic |
| 🤖 IA | OpenAI API (GPT-4o) con tool calling |
| 🖥️ Frontend | Streamlit |
| 🐳 Contenedores | Docker y Docker Compose |
| ✅ Validacion | Pydantic v2 |

---

## 🗃️ Modelo de datos

Cada tarea contiene:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | int | Identificador unico (auto-increment) |
| `title` | str | Titulo de la tarea (obligatorio) |
| `description` | str | Descripcion opcional |
| `status` | enum | `pending`, `in_progress`, `completed` |
| `priority` | enum | `low`, `medium`, `high` |
| `due_date` | datetime | Fecha limite |
| `created_at` | datetime | Fecha de creacion (automatica) |
| `updated_at` | datetime | Ultima actualizacion (automatica) |

---

## 🔌 Endpoints

### 📝 Tareas — `/api/tasks`

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `POST` | `/api/tasks` | Crear una tarea |
| `GET` | `/api/tasks` | Listar tareas con filtros opcionales (`status`, `priority`, `date_from`, `date_to`) |
| `GET` | `/api/tasks/{id}` | Obtener detalle de una tarea |
| `PUT` | `/api/tasks/{id}` | Actualizar una tarea |
| `DELETE` | `/api/tasks/{id}` | Eliminar una tarea |

### 🤖 Agente IA — `/api/agent`

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `POST` | `/api/agent/chat` | Enviar mensaje en lenguaje natural al agente |
| `DELETE` | `/api/agent/history` | Limpiar historial de conversacion |

### 📊 Resumen — `/api/summary`

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/api/summary/today` | Resumen del dia con estadisticas y analisis IA |
| `GET` | `/api/summary/weekly-completed` | Tareas completadas por dia (semana actual) |

---

## 🤖 Agente IA

El agente interpreta instrucciones en lenguaje natural y ejecuta acciones sobre las tareas usando **tool calling** de OpenAI. Cuenta con 10 herramientas:

| Herramienta | Descripcion |
|-------------|-------------|
| `create_task` | ➕ Crear una nueva tarea |
| `list_tasks` | 📋 Listar tareas con filtros |
| `get_task` | 🔍 Obtener detalle de una tarea por ID |
| `update_task` | ✏️ Actualizar campos de una tarea |
| `delete_task` | 🗑️ Eliminar una tarea por ID |
| `bulk_update_status` | 🔄 Cambiar estado de multiples tareas por filtro |
| `bulk_delete` | 🗑️ Eliminar multiples tareas por filtro |
| `count_tasks` | 🔢 Contar tareas con filtros |
| `get_most_urgent` | 🚨 Obtener la tarea mas urgente |
| `get_overdue_tasks` | ⏰ Obtener tareas vencidas |

### 💬 Ejemplos de instrucciones

> *"Crea una tarea llamada 'Revisar propuesta' con prioridad alta para el viernes"*
>
> *"¿Cuantas tareas tengo pendientes esta semana?"*
>
> *"Marca como completadas todas las tareas de prioridad baja"*
>
> *"¿Cual es la tarea mas urgente que tengo?"*
>
> *"Elimina todas las tareas que ya estan completadas"*

El historial de conversacion se mantiene en memoria por `session_id` mientras el servidor esta activo.

---

## 📊 Resumen del dia

El endpoint `GET /api/summary/today` retorna:

- 📈 **Estadisticas:** tareas totales, distribucion por estado y prioridad, tareas vencidas, que vencen hoy y esta semana.
- 🧠 **Analisis:** texto generado por IA con un diagnostico del estado actual y sugerencias de priorizacion.

---

## 🖥️ Frontend

Interfaz web con Streamlit organizada en 3 pestanas:

| Pestana | Descripcion |
|---------|-------------|
| 📝 **Tareas** | Lista de tareas con filtros, creacion desde sidebar, edicion inline y eliminacion |
| 🤖 **Agente IA** | Chat interactivo con el agente. Muestra las acciones ejecutadas |
| 📊 **Resumen del dia** | Dashboard con grafico de completadas por dia, estadisticas y analisis IA |

---

## 📄 Documentacion

La API cuenta con documentacion interactiva generada automaticamente por FastAPI:

| Recurso | URL | Descripcion |
|---------|-----|-------------|
| 📘 Swagger UI | `http://localhost:8000/docs` | Documentacion interactiva con interfaz para probar cada endpoint directamente desde el navegador |
| 📕 ReDoc | `http://localhost:8000/redoc` | Documentacion alternativa con vista de referencia detallada |
| 📦 OpenAPI JSON | `http://localhost:8000/openapi.json` | Esquema OpenAPI 3.1 en formato JSON para integraciones externas |

Todos los endpoints incluyen descripciones, ejemplos de request/response y codigos de estado documentados.

---

## 🚀 Instalacion y ejecucion

### 🐳 Con Docker (recomendado)

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/<tu-usuario>/TaskMind.git
   cd TaskMind
   ```

2. Crear el archivo `.env` a partir del ejemplo:
   ```bash
   cp .env.example .env
   ```

3. Configurar las variables en `.env`:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:1234@db:5432/taskmind
   OPENAI_API_KEY=sk-proj-...
   OPENAI_MODEL=gpt-4o
   ```

4. Levantar los servicios:
   ```bash
   docker compose up --build
   ```

5. Acceder a:
   - 🌐 API: `http://localhost:8000`
   - 📘 Swagger: `http://localhost:8000/docs`
   - 🖥️ Frontend: `http://localhost:8501`

### 💻 Sin Docker

1. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar `.env` con la URL de una base de datos PostgreSQL local:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/taskmind
   OPENAI_API_KEY=sk-proj-...
   OPENAI_MODEL=gpt-4o
   ```

4. Ejecutar migraciones:
   ```bash
   alembic upgrade head
   ```

5. Iniciar el backend:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Iniciar el frontend (en otra terminal):
   ```bash
   streamlit run frontend/app.py
   ```

---

## 📁 Estructura del proyecto

```
TaskMind/
├── 📂 app/
│   ├── main.py              # Inicializacion de FastAPI
│   ├── config.py            # Variables de entorno (Pydantic Settings)
│   ├── database.py          # Engine y sesion async de SQLAlchemy
│   ├── 📂 models/
│   │   └── task.py          # Modelo ORM de tarea
│   ├── 📂 schemas/
│   │   └── task.py          # Schemas de validacion (Pydantic)
│   ├── 📂 routers/
│   │   ├── tasks.py         # Endpoints CRUD de tareas
│   │   ├── agent.py         # Endpoint del agente IA
│   │   └── summary.py       # Endpoint de resumen del dia
│   ├── 📂 services/
│   │   ├── task_service.py  # Logica de negocio de tareas
│   │   └── agent_service.py # Integracion con OpenAI y loop de herramientas
│   └── 📂 agent/
│       ├── tools.py         # Definiciones de herramientas para OpenAI
│       ├── prompts.py       # System prompt del agente
│       └── memory.py        # Historial de conversacion en memoria
├── 📂 frontend/
│   ├── app.py               # App principal de Streamlit
│   ├── api.py               # Cliente HTTP para el backend
│   ├── styles.py            # Estilos CSS
│   └── 📂 components/
│       ├── sidebar.py       # Filtros y formulario de creacion
│       ├── task_list.py     # Lista de tareas con edicion
│       ├── chat.py          # Chat con el agente
│       └── summary.py       # Dashboard de resumen
├── 📂 alembic/              # Migraciones de base de datos
├── 🐳 Dockerfile
├── 🐳 docker-compose.yml
├── entrypoint.sh
├── requirements.txt
└── .env.example
```

---

## 🧪 Tests

El proyecto cuenta con **124 pruebas unitarias** y de integracion que cubren el **90% del codigo** del backend.

### Ejecutar los tests

1. Instalar las dependencias de testing:
   ```bash
   pip install -r requirements-test.txt
   ```

2. Ejecutar los tests:
   ```bash
   pytest
   ```

3. Ejecutar con reporte de coverage:
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```

### Estructura de tests

```
tests/
├── conftest.py              # Fixtures compartidos (DB SQLite en memoria, cliente HTTP)
├── test_models.py           # Modelo Task, enums TaskStatus y TaskPriority
├── test_schemas.py          # Schemas Pydantic (TaskCreate, TaskUpdate, TaskResponse, TaskFilters)
├── test_memory.py           # Historial de conversacion en memoria
├── test_prompts.py          # Generacion del system prompt del agente
├── test_tools.py            # Definiciones de herramientas de OpenAI
├── test_task_service.py     # Logica de negocio (CRUD, bulk, conteo, urgentes, vencidas, resumen)
├── test_agent_service.py    # Serializacion, ejecucion de herramientas y flujo de chat
├── test_routers_tasks.py    # Endpoints CRUD de tareas (validaciones, filtros, 404)
├── test_routers_agent.py    # Endpoints del agente IA (chat, limpiar historial)
├── test_routers_summary.py  # Endpoints de resumen (semanal, diario con mock de OpenAI)
└── test_main.py             # Health check, configuracion de la app y schema OpenAPI
```

### Coverage por modulo

| Modulo | Coverage |
|--------|----------|
| `models/`, `schemas/`, `agent/memory`, `agent/prompts`, `agent/tools` | 100% |
| `config.py`, `routers/agent.py`, `routers/tasks.py` | 100% |
| `routers/summary.py` | 92% |
| `main.py`, `services/agent_service.py` | 90% |
| `database.py` | 80% |

> Los tests usan **SQLite async en memoria** como base de datos y **mocks** para las llamadas a OpenAI, por lo que no requieren servicios externos para ejecutarse.

---

## 🧩 Decisiones tecnicas

- ⚡ **Arquitectura async:** Se utiliza SQLAlchemy en modo async con asyncpg para maximizar el rendimiento en operaciones I/O-bound.
- 🔧 **Tool calling de OpenAI:** El agente usa el mecanismo nativo de tool calling en lugar de parsear texto, lo que garantiza ejecuciones estructuradas y confiables.
- 💾 **Historial en memoria:** El historial de conversacion se almacena en un diccionario en memoria segmentado por `session_id`, cumpliendo el requerimiento de no persistir en base de datos.
- 🔄 **Operaciones bulk:** Se implementaron herramientas de actualizacion y eliminacion masiva para que el agente pueda ejecutar instrucciones como "marca todas las tareas de prioridad baja como completadas" en una sola operacion.
- 📊 **Resumen con IA:** El endpoint de resumen combina estadisticas calculadas desde la base de datos con un analisis generado por OpenAI, proporcionando tanto datos estructurados como interpretacion en lenguaje natural.
