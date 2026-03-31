from app.agent.tools import TOOL_DEFINITIONS


class TestToolDefinitions:
    def test_is_list(self):
        assert isinstance(TOOL_DEFINITIONS, list)

    def test_has_10_tools(self):
        assert len(TOOL_DEFINITIONS) == 10

    def test_all_have_type_function(self):
        for tool in TOOL_DEFINITIONS:
            assert tool["type"] == "function"

    def test_all_have_function_key(self):
        for tool in TOOL_DEFINITIONS:
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]

    def test_expected_tool_names(self):
        names = {t["function"]["name"] for t in TOOL_DEFINITIONS}
        expected = {
            "create_task", "list_tasks", "get_task", "update_task",
            "delete_task", "bulk_update_status", "bulk_delete",
            "count_tasks", "get_most_urgent", "get_overdue_tasks",
        }
        assert names == expected

    def test_create_task_requires_title(self):
        create = next(t for t in TOOL_DEFINITIONS if t["function"]["name"] == "create_task")
        assert "title" in create["function"]["parameters"]["required"]

    def test_parameters_have_properties(self):
        for tool in TOOL_DEFINITIONS:
            params = tool["function"]["parameters"]
            assert params["type"] == "object"
            assert "properties" in params
