import json

import streamlit as st

from frontend import api


def render():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("actions"):
                _render_actions(msg["actions"])

    if prompt := st.chat_input("Escribe un mensaje al agente..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                data = api.agent_chat(prompt)

            if data:
                st.write(data["response"])
                actions = data.get("actions_taken", [])
                if actions:
                    _render_actions(actions)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": data["response"],
                    "actions": actions,
                })
            else:
                st.error("No se pudo conectar con el agente.")

    if st.button("Limpiar historial"):
        api.agent_clear_history()
        st.session_state.chat_history = []
        st.rerun()


def _render_actions(actions: list):
    summary_lines = []
    for a in actions:
        args_str = ", ".join(f"{k}={v}" for k, v in a["arguments"].items())
        summary_lines.append(f"**{a['tool']}**({args_str})")

    content = "<br>".join(summary_lines)
    st.markdown(f'<div class="actions-box">{content}</div>', unsafe_allow_html=True)
