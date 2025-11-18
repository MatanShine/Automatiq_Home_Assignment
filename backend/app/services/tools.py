"""
OpenAI tool definitions for the LLM to use.
"""

CHECK_IF_EMPLOYEE_EXISTS_BY_ID_AND_NAME = {
    "type": "function",
    "name": "check_if_employee_exists_by_id_and_name",
    "description": "Check if an employee exists in the database by their employee ID and employee name. Use this tool to verify employee credentials before allowing access.",
    "parameters": {
        "type": "object",
        "properties": {
            "employee_id": {
                "type": "string",
                "description": "The unique employee ID to check"
            },
            "employee_name": {
                "type": "string",
                "description": "The employee's name to check"
            }
        },
        "required": ["employee_id", "employee_name"]
    }
}

