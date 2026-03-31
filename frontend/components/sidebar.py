import streamlit as st
from datetime import datetime

from frontend import api
from frontend.styles import STATUS_LABELS, PRIORITY_LABELS


def render() -> dict:
    """Render sidebar with compact filters and create form. Returns active filters."""
    with st.sidebar:
        st.markdown("### Filtros")
        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox(
                "Estado",
                [None, "pending", "in_progress", "completed"],
                format_func=lambda x: "Todos" if x is None else STATUS_LABELS.get(x, x),
            )
        with col2:
            priority = st.selectbox(
                "Prioridad",
                [None, "low", "medium", "high"],
                format_func=lambda x: "Todas" if x is None else PRIORITY_LABELS.get(x, x),
            )

        col_from, col_to = st.columns(2)
        with col_from:
            date_from = st.date_input("Desde", value=None, key="filter_date_from")
        with col_to:
            date_to = st.date_input("Hasta", value=None, key="filter_date_to")

        st.markdown("---")
        st.markdown("### Nueva tarea")
        with st.form("create_task_form", clear_on_submit=True):
            title = st.text_input("Titulo")
            desc = st.text_area("Descripcion", height=60)
            c1, c2 = st.columns(2)
            with c1:
                prio = st.selectbox(
                    "Prioridad",
                    ["medium", "low", "high"],
                    format_func=lambda x: PRIORITY_LABELS.get(x, x),
                    key="new_p",
                )
            with c2:
                due = st.date_input("Fecha limite", value=None)
            submitted = st.form_submit_button("Crear", use_container_width=True)

            if submitted and title:
                payload = {"title": title, "description": desc or None, "priority": prio}
                if due:
                    payload["due_date"] = datetime.combine(due, datetime.min.time()).isoformat()
                r = api.create_task(payload)
                if r.status_code == 201:
                    st.toast("Tarea creada correctamente", icon="✅")
                    st.rerun()
                else:
                    st.toast("Error al crear tarea", icon="❌")

    params = {}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if date_from:
        params["date_from"] = datetime.combine(date_from, datetime.min.time()).isoformat()
    if date_to:
        params["date_to"] = datetime.combine(date_to, datetime.max.time()).isoformat()
    return params
