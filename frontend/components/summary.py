import streamlit as st
import pandas as pd

from frontend import api
from frontend.styles import PRIORITY_LABELS, STATUS_LABELS

MONTH_NAMES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}


def _render_monthly_chart():
    data = api.get_monthly_created()
    if not data:
        st.info("No hay datos para mostrar.")
        return

    df = pd.DataFrame(data)
    df["month_date"] = pd.to_datetime(df["month"] + "-01")
    df["label"] = df["month_date"].dt.month.map(MONTH_NAMES) + " " + df["month_date"].dt.year.astype(str).str[-2:]
    df = df.set_index("label")

    st.markdown("#### Tareas creadas por mes (5 meses)")
    st.bar_chart(df["count"], color="#0984e3")


def render():
    _render_monthly_chart()

    st.markdown("---")

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
