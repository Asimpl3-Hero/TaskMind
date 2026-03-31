import streamlit as st

PRIORITY_LABELS = {"high": "Alta", "medium": "Media", "low": "Baja"}
STATUS_LABELS = {"pending": "Pendiente", "in_progress": "En progreso", "completed": "Completada"}


def inject_css():
    st.markdown("""
    <style>
        /* --- Global --- */
        section[data-testid="stSidebar"] {
            width: 280px !important;
            min-width: 280px !important;
        }
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stTextInput label,
        section[data-testid="stSidebar"] .stTextArea label,
        section[data-testid="stSidebar"] .stDateInput label {
            font-size: 0.82rem;
            margin-bottom: 0;
        }
        section[data-testid="stSidebar"] .stSelectbox,
        section[data-testid="stSidebar"] .stTextInput,
        section[data-testid="stSidebar"] .stTextArea,
        section[data-testid="stSidebar"] .stDateInput {
            margin-bottom: 0.15rem;
        }
        section[data-testid="stSidebar"] textarea {
            height: 60px !important;
            min-height: 60px !important;
        }

        /* --- Priority badges --- */
        .badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.78rem;
            font-weight: 600;
            color: #fff;
        }
        .badge-high { background: #e74c3c; }
        .badge-medium { background: #f39c12; }
        .badge-low { background: #27ae60; }

        .badge-pending { background: #636e72; }
        .badge-in_progress { background: #0984e3; }
        .badge-completed { background: #00b894; }

        /* --- Task card --- */
        .task-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.6rem;
            background: var(--secondary-background-color);
        }
        .task-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.3rem;
        }
        .task-card-title {
            font-weight: 600;
            font-size: 1rem;
        }
        .task-card-meta {
            font-size: 0.82rem;
            color: #888;
        }

        /* --- Summary metric --- */
        div[data-testid="stMetric"] {
            background: var(--secondary-background-color);
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 0.8rem;
        }

        /* --- Overdue tasks --- */
        .task-card-overdue {
            border: 1px solid #e74c3c !important;
            border-left: 4px solid #e74c3c !important;
            background: rgba(231, 76, 60, 0.06);
        }
        .badge-overdue {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.78rem;
            font-weight: 600;
            color: #fff;
            background: #e74c3c;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        /* --- Chat --- */
        .actions-box {
            background: var(--secondary-background-color);
            border-left: 3px solid #00b894;
            padding: 0.6rem 0.8rem;
            border-radius: 4px;
            font-size: 0.85rem;
            margin-top: 0.4rem;
        }
        .actions-box-error {
            background: rgba(231, 76, 60, 0.06);
            border-left: 3px solid #e74c3c;
            padding: 0.6rem 0.8rem;
            border-radius: 4px;
            font-size: 0.85rem;
            margin-top: 0.4rem;
        }
    </style>
    """, unsafe_allow_html=True)


def priority_badge(priority: str) -> str:
    return f'<span class="badge badge-{priority}">{PRIORITY_LABELS.get(priority, priority)}</span>'


def status_badge(status: str) -> str:
    return f'<span class="badge badge-{status}">{STATUS_LABELS.get(status, status)}</span>'
