import streamlit as st

from frontend import api
from frontend.styles import PRIORITY_LABELS, STATUS_LABELS


def render():
    if st.button("Generar resumen del dia"):
        with st.spinner("Generando resumen..."):
            data = api.get_summary()

        if not data:
            st.error("No se pudo obtener el resumen.")
            return

        stats = data["statistics"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", stats["total_tasks"])
        c2.metric("Vencidas", stats["overdue"])
        c3.metric("Vencen hoy", stats["due_today"])
        c4.metric("Esta semana", stats["due_this_week"])

        st.markdown("---")

        col_s, col_p = st.columns(2)
        with col_s:
            st.markdown("#### Por estado")
            for k, v in stats["by_status"].items():
                st.write(f"**{STATUS_LABELS.get(k, k)}:** {v}")
        with col_p:
            st.markdown("#### Por prioridad")
            for k, v in stats["by_priority"].items():
                st.write(f"**{PRIORITY_LABELS.get(k, k)}:** {v}")

        st.markdown("---")
        st.markdown("#### Analisis del agente")
        st.write(data["analysis"])
