from app.services.llm import llm_formatters


def test_format_json_output_returns_error_when_empty():
    result = llm_formatters.format_json_output(None, "missing")
    assert result == '{"error": "missing"}'


def test_format_employees_by_status_formats_payload():
    employees = [("1", "John", "Doe", "Division")]
    formatted = llm_formatters.format_employees_by_status(employees)
    assert formatted["count"] == 1
    assert formatted["employees"][0]["employee_id"] == "1"


def test_format_employees_by_status_with_no_employees():
    formatted = llm_formatters.format_employees_by_status([])
    assert formatted == {"error": "No employees found with this status", "employees": [], "count": 0}
