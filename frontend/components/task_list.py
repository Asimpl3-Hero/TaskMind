from datetime import datetime

import streamlit as st

from frontend import api
from frontend.styles import PRIORITY_LABELS, STATUS_LABELS, priority_badge, status_badge


STATUSES = ["pending", "in_progress", "completed"]
PRIORITIES = ["low", "medium", "high"]
TASKS_PER_PAGE = 10

SORT_OPTIONS = {
    "Fecha de creacion": "created_at",
    "Fecha de vencimiento": "due_date",
    "Prioridad": "priority",
}

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _is_overdue(task: dict) -> bool:
    if not task.get("due_date") or task.get("status") == "completed":
        return False
    return task["due_date"][:10] < datetime.utcnow().strftime("%Y-%m-%d")


def _sort_tasks(tasks: list[dict], sort_key: str) -> list[dict]:
    if sort_key == "priority":
        return sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t.get("priority"), 99))
    if sort_key == "due_date":
        return sorted(tasks, key=lambda t: t.get("due_date") or "9999-12-31")
    return sorted(tasks, key=lambda t: t.get("created_at") or "")


def _render_feedback(task_id: int) -> None:
    flash_key = f"task_feedback_{task_id}"
    flash = st.session_state.pop(flash_key, None)
    if not flash:
        return

    level = flash.get("level")
    text = flash.get("text", "")
    if level == "success":
        st.success(text)
    elif level == "error":
        st.error(text)
    else:
        st.info(text)


def _set_feedback(task_id: int, level: str, text: str) -> None:
    st.session_state[f"task_feedback_{task_id}"] = {"level": level, "text": text}


def render(filters: dict):
    tasks = api.get_tasks(filters)

    if not tasks:
        st.info("No hay tareas para mostrar.")
        return

    col_count, col_sort = st.columns([3, 2])
    with col_count:
        st.markdown(f"**Mostrando {len(tasks)} tarea{'s' if len(tasks) != 1 else ''}**")
    with col_sort:
        sort_label = st.selectbox(
            "Ordenar por",
            list(SORT_OPTIONS.keys()),
            key="task_sort",
            label_visibility="collapsed",
        )

    sort_key = SORT_OPTIONS[sort_label]
    tasks = _sort_tasks(tasks, sort_key)

    total_pages = max(1, -(-len(tasks) // TASKS_PER_PAGE))
    if "task_page" not in st.session_state:
        st.session_state.task_page = 1
    st.session_state.task_page = min(st.session_state.task_page, total_pages)

    start = (st.session_state.task_page - 1) * TASKS_PER_PAGE
    page_tasks = tasks[start : start + TASKS_PER_PAGE]

    for task in page_tasks:
        overdue = _is_overdue(task)
        due = task["due_date"][:10] if task.get("due_date") else "Sin fecha"

        overdue_class = " task-card-overdue" if overdue else ""
        overdue_label = '<span class="badge-overdue">Vencida</span>' if overdue else ""

        header_html = (
            f'<div class="task-card{overdue_class}">'
            f'<div class="task-card-header">'
            f'<span class="task-card-title">{task["title"]}</span>'
            f'<span>{overdue_label} {priority_badge(task["priority"])} {status_badge(task["status"])}</span>'
            f"</div>"
            f'<div class="task-card-meta">'
            f'Vence: {due} &middot; Creada: {task["created_at"][:10]}'
            f"</div>"
            f"</div>"
        )

        prefix = "[Vencida] " if overdue else ""
        with st.expander(
            f'{prefix}{task["title"]} - {due} | {STATUS_LABELS.get(task["status"], task["status"])}'
        ):
            st.markdown(header_html, unsafe_allow_html=True)
            if task.get("description"):
                st.caption(task["description"])

            _render_feedback(task["id"])

            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
            with c1:
                new_status = st.selectbox(
                    "Estado",
                    STATUSES,
                    index=STATUSES.index(task["status"]),
                    format_func=lambda x: STATUS_LABELS.get(x, x),
                    key=f"st_{task['id']}",
                )
            with c2:
                new_prio = st.selectbox(
                    "Prioridad",
                    PRIORITIES,
                    index=PRIORITIES.index(task["priority"]),
                    format_func=lambda x: PRIORITY_LABELS.get(x, x),
                    key=f"pr_{task['id']}",
                )
            with c3:
                st.write("")
                if st.button("Guardar", key=f"save_{task['id']}", use_container_width=True):
                    with st.spinner("Guardando cambios..."):
                        response = api.update_task(task["id"], {"status": new_status, "priority": new_prio})
                    if response.status_code == 200:
                        _set_feedback(task["id"], "success", "Cambios guardados correctamente.")
                    else:
                        _set_feedback(task["id"], "error", "No se pudo guardar. Intenta de nuevo.")
                    st.rerun()
            with c4:
                st.write("")
                if st.button("Eliminar", key=f"del_{task['id']}", type="primary", use_container_width=True):
                    st.session_state[f"confirm_del_{task['id']}"] = True
                    _set_feedback(task["id"], "info", "Confirma la eliminacion para continuar.")
                    st.rerun()

            if st.session_state.get(f"confirm_del_{task['id']}"):
                st.warning(f"Seguro que deseas eliminar: {task['title']}?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Si, eliminar", key=f"yes_del_{task['id']}", use_container_width=True):
                        with st.spinner("Eliminando tarea..."):
                            response = api.delete_task(task["id"])
                        del st.session_state[f"confirm_del_{task['id']}"]
                        if response.status_code == 204:
                            st.toast("Tarea eliminada")
                            st.rerun()
                        else:
                            _set_feedback(task["id"], "error", "No se pudo eliminar la tarea.")
                            st.rerun()
                with col_no:
                    if st.button("Cancelar", key=f"no_del_{task['id']}", use_container_width=True):
                        del st.session_state[f"confirm_del_{task['id']}"]
                        _set_feedback(task["id"], "info", "Eliminacion cancelada.")
                        st.rerun()

    if total_pages > 1:
        st.markdown("---")
        col_prev, col_info, col_next = st.columns([1, 2, 1])
        with col_info:
            st.markdown(
                f"<div style='text-align:center'>Pagina {st.session_state.task_page} de {total_pages}</div>",
                unsafe_allow_html=True,
            )
        with col_prev:
            if st.button("Anterior", disabled=st.session_state.task_page <= 1, use_container_width=True):
                st.session_state.task_page -= 1
                st.rerun()
        with col_next:
            if st.button("Siguiente", disabled=st.session_state.task_page >= total_pages, use_container_width=True):
                st.session_state.task_page += 1
                st.rerun()
