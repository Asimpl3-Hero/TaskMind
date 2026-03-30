import streamlit as st
from datetime import datetime

from frontend import api


def render() -> dict:
    """Render sidebar with compact filters and create form. Returns active filters."""
    with st.sidebar:
        st.markdown("### Filtros")
        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox(
                "Estado",
                [None, "pending", "in_progress", "completed"],
                format_func=lambda x: "Todos" if x is None else x,
            )
        with col2:
            priority = st.selectbox(
                "Prioridad",
                [None, "low", "medium", "high"],
                format_func=lambda x: "Todas" if x is None else x,
            )

        st.markdown("---")
        st.markdown("### Nueva tarea")
        with st.form("create_task_form", clear_on_submit=True):
            title = st.text_input("Titulo")
            desc = st.text_area("Descripcion", height=60)
            c1, c2 = st.columns(2)
            with c1:
                prio = st.selectbox("Prioridad", ["medium", "low", "high"], key="new_p")
            with c2:
                due = st.date_input("Fecha limite", value=None)
            submitted = st.form_submit_button("Crear", use_container_width=True)

            if submitted and title:
                payload = {"title": title, "description": desc or None, "priority": prio}
                if due:
                    payload["due_date"] = datetime.combine(due, datetime.min.time()).isoformat()
                r = api.create_task(payload)
                if r.status_code == 201:
                    st.success("Tarea creada")
                    st.rerun()
                else:
                    st.error("Error al crear tarea")

    params = {}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    return params
