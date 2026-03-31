from app.agent import memory


class TestMemory:
    def setup_method(self):
        memory.conversations.clear()

    def test_get_history_empty(self):
        history = memory.get_history("sess1")
        assert history == []

    def test_add_and_get_message(self):
        memory.add_message("sess1", {"role": "user", "content": "hi"})
        history = memory.get_history("sess1")
        assert len(history) == 1
        assert history[0]["content"] == "hi"

    def test_multiple_messages(self):
        memory.add_message("sess1", {"role": "user", "content": "a"})
        memory.add_message("sess1", {"role": "assistant", "content": "b"})
        assert len(memory.get_history("sess1")) == 2

    def test_separate_sessions(self):
        memory.add_message("s1", {"role": "user", "content": "hello"})
        memory.add_message("s2", {"role": "user", "content": "world"})
        assert len(memory.get_history("s1")) == 1
        assert len(memory.get_history("s2")) == 1
        assert memory.get_history("s1")[0]["content"] == "hello"

    def test_clear_history(self):
        memory.add_message("sess1", {"role": "user", "content": "hi"})
        memory.clear_history("sess1")
        # After clear, get_history creates a new empty list
        assert memory.get_history("sess1") == []

    def test_clear_nonexistent_session(self):
        # Should not raise
        memory.clear_history("nonexistent")

    def test_default_session(self):
        memory.add_message("default", {"role": "user", "content": "msg"})
        assert len(memory.get_history("default")) == 1
