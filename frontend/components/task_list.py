import streamlit as st

from frontend import api
from frontend.styles import priority_badge, status_badge, STATUS_LABELS


STATUSES = ["pending", "in_progress", "completed"]
PRIORITIES = ["low", "medium", "high"]


def render(filters: dict):
    tasks = api.get_tasks(filters)

    if not tasks:
        st.info("No hay tareas para mostrar.")
        return

    for task in tasks:
        due = task["due_date"][:10] if task["due_date"] else "Sin fecha"
        header_html = (
            f'<div class="task-card"><div class="task-card-header">'
            f'<span class="task-card-title">{task["title"]}</span>'
            f'<span>{priority_badge(task["priority"])} {status_badge(task["status"])}</span>'
            f'</div>'
            f'<div class="task-card-meta">'
            f'Vence: {due} &nbsp;&middot;&nbsp; Creada: {task["created_at"][:10]}'
            f'</div></div>'
        )

        with st.expander(f'{task["title"]}  —  {due}  |  {STATUS_LABELS.get(task["status"], task["status"])}'):
            st.markdown(header_html, unsafe_allow_html=True)

            if task["description"]:
                st.caption(task["description"])

            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
            with c1:
                new_status = st.selectbox(
                    "Estado",
                    STATUSES,
                    index=STATUSES.index(task["status"]),
                    key=f"st_{task['id']}",
                )
            with c2:
                new_prio = st.selectbox(
                    "Prioridad",
                    PRIORITIES,
                    index=PRIORITIES.index(task["priority"]),
                    key=f"pr_{task['id']}",
                )
            with c3:
                st.write("")
                if st.button("Guardar", key=f"save_{task['id']}", use_container_width=True):
                    r = api.update_task(task["id"], {"status": new_status, "priority": new_prio})
                    if r.status_code == 200:
                        st.rerun()
                    else:
                        st.error("Error al actualizar la tarea.")
            with c4:
                st.write("")
                if st.button("Eliminar", key=f"del_{task['id']}", type="primary", use_container_width=True):
                    r = api.delete_task(task["id"])
                    if r.status_code == 204:
                        st.rerun()
                    else:
                        st.error("Error al eliminar la tarea.")
