import sys
from pathlib import Path

# Ensure project root is in path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from frontend.styles import inject_css
from frontend.components import sidebar, task_list, chat, summary

st.set_page_config(page_title="TaskMind", layout="wide")
inject_css()

st.markdown("# TaskMind")
st.caption("Sistema de gestion de tareas con agente IA")

filters = sidebar.render()

tab_tasks, tab_chat, tab_summary = st.tabs(["Tareas", "Agente IA", "Resumen del dia"])

with tab_tasks:
    task_list.render(filters)

with tab_chat:
    chat.render()

with tab_summary:
    summary.render()
