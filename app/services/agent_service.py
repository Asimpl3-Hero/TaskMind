import json
import logging

from fastapi import HTTPException
from openai import AsyncOpenAI, APIConnectionError, RateLimitError, APIStatusError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.agent.prompts import get_system_prompt
from app.agent.tools import TOOL_DEFINITIONS
from app.agent import memory
from app.exceptions import ExternalServiceError, AgentTimeoutError
from app.models.task import TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilters
from app.services import task_service

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

MAX_AGENT_ITERATIONS = 10


def _serialize_task(task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority.value,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


async def execute_tool(tool_name: str, arguments: dict, db: AsyncSession) -> str:
    try:
        result = await _run_tool(tool_name, arguments, db)
        return json.dumps(result, ensure_ascii=False)
    except HTTPException as e:
        return json.dumps({"error": e.detail}, ensure_ascii=False)
    except (ValidationError, ValueError, KeyError) as e:
        logger.warning("Error de validacion en tool '%s': %s", tool_name, e)
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def _run_tool(tool_name: str, args: dict, db: AsyncSession):
    if tool_name == "create_task":
        data = TaskCreate(
            title=args["title"],
            description=args.get("description"),
            priority=args.get("priority", "medium"),
            due_date=args.get("due_date"),
        )
        task = await task_service.create_task(db, data)
        return _serialize_task(task)

    if tool_name == "list_tasks":
        filters = TaskFilters(
            status=args.get("status"),
            priority=args.get("priority"),
            date_from=args.get("date_from"),
            date_to=args.get("date_to"),
        )
        tasks = await task_service.get_tasks(db, filters)
        return [_serialize_task(t) for t in tasks]

    if tool_name == "get_task":
        task = await task_service.get_task(db, args["task_id"])
        return _serialize_task(task)

    if tool_name == "update_task":
        task_id = args.pop("task_id")
        data = TaskUpdate(**args)
        task = await task_service.update_task(db, task_id, data)
        return _serialize_task(task)

    if tool_name == "delete_task":
        await task_service.delete_task(db, args["task_id"])
        return {"deleted": True, "task_id": args["task_id"]}

    if tool_name == "bulk_update_status":
        count = await task_service.bulk_update_status(
            db,
            new_status=TaskStatus(args["new_status"]),
            status_filter=TaskStatus(args["status_filter"]) if args.get("status_filter") else None,
            priority_filter=TaskPriority(args["priority_filter"]) if args.get("priority_filter") else None,
        )
        return {"updated_count": count, "new_status": args["new_status"]}

    if tool_name == "bulk_delete":
        count = await task_service.bulk_delete(
            db,
            status_filter=TaskStatus(args["status_filter"]) if args.get("status_filter") else None,
            priority_filter=TaskPriority(args["priority_filter"]) if args.get("priority_filter") else None,
        )
        return {"deleted_count": count}

    if tool_name == "count_tasks":
        filters = TaskFilters(
            status=args.get("status"),
            priority=args.get("priority"),
            date_from=args.get("date_from"),
            date_to=args.get("date_to"),
        )
        count = await task_service.count_tasks(db, filters)
        return {"count": count}

    if tool_name == "get_most_urgent":
        task = await task_service.get_most_urgent(db)
        if task:
            return _serialize_task(task)
        return {"message": "No hay tareas urgentes pendientes"}

    if tool_name == "get_overdue_tasks":
        tasks = await task_service.get_overdue_tasks(db)
        return [_serialize_task(t) for t in tasks]

    return {"error": f"Tool '{tool_name}' no reconocida"}


async def chat(message: str, session_id: str, db: AsyncSession) -> dict:
    memory.add_message(session_id, {"role": "user", "content": message})

    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.extend(memory.get_history(session_id))

    actions_taken = []

    for _ in range(MAX_AGENT_ITERATIONS):
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
        except APIConnectionError:
            logger.error("No se pudo conectar con OpenAI en agent chat")
            raise ExternalServiceError("OpenAI", "no se pudo establecer conexion")
        except RateLimitError:
            logger.warning("Rate limit alcanzado en OpenAI en agent chat")
            raise ExternalServiceError("OpenAI", "limite de solicitudes excedido, intente mas tarde")
        except APIStatusError as e:
            logger.error("Error de API OpenAI (status %s): %s", e.status_code, e.message)
            raise ExternalServiceError("OpenAI", f"error del servicio (status {e.status_code})")

        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" or choice.message.tool_calls:
            assistant_msg = choice.message.model_dump()
            messages.append(assistant_msg)
            memory.add_message(session_id, assistant_msg)

            for tool_call in choice.message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                result = await execute_tool(fn_name, fn_args, db)

                actions_taken.append({
                    "tool": fn_name,
                    "arguments": fn_args,
                    "result": json.loads(result),
                })

                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
                messages.append(tool_msg)
                memory.add_message(session_id, tool_msg)
        else:
            reply = choice.message.content
            memory.add_message(session_id, {"role": "assistant", "content": reply})
            return {"response": reply, "actions_taken": actions_taken}

    logger.error("Agente excedio %d iteraciones para session '%s'", MAX_AGENT_ITERATIONS, session_id)
    raise AgentTimeoutError(MAX_AGENT_ITERATIONS)
