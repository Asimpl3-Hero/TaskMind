from app.agent.prompts import get_system_prompt


class TestPrompts:
    def test_returns_string(self):
        prompt = get_system_prompt()
        assert isinstance(prompt, str)

    def test_contains_key_elements(self):
        prompt = get_system_prompt()
        assert "TaskMind" in prompt
        assert "español" in prompt
        assert "herramientas" in prompt or "tools" in prompt

    def test_contains_date(self):
        prompt = get_system_prompt()
        # Should contain current date/time info
        assert "Fecha y hora actual" in prompt

    def test_contains_weekday(self):
        prompt = get_system_prompt()
        # Weekday names in English (from strftime %A)
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        assert any(day in prompt for day in weekdays)
