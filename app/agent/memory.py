conversations: dict[str, list] = {}


def get_history(session_id: str = "default") -> list:
    return conversations.setdefault(session_id, [])


def add_message(session_id: str, message: dict) -> None:
    conversations.setdefault(session_id, []).append(message)


def clear_history(session_id: str = "default") -> None:
    conversations.pop(session_id, None)
