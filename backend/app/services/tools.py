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

FETCH_CURRENT_EMPLOYEE_DATA = {
    "type": "function",
    "name": "fetch_all_current_user_data",
    "description": "Fetch the current employee's data including personal information and training video completion status. Use this tool when the employee asks about their own information or training progress.",
}

FETCH_CURRENT_EMPLOYEE_TRAINING_STATUS = {
    "type": "function",
    "name": "fetch_current_employee_training_status",
    "description": "Fetch the current employee's training status (NOT_STARTED, IN_PROGRESS, or FINISHED). Use this tool when the employee asks about their training status or completion status.",
}

GET_STATISTIC_SUMMARY_ON_TRAINING = {
    "type": "function",
    "name": "get_statistic_summary_on_training",
    "description": "Get a comprehensive statistical summary of training progress including counts of finished, in-progress, and not-started employees, as well as timing statistics. Use this tool when the CISO asks about overall training statistics or progress metrics.",
}

FETCH_CURRENT_CISO_EMPLOYEE_DATA = {
    "type": "function",
    "name": "fetch_current_ciso_employee_data",
    "description": "Fetch the CISO's own employee data including personal information and training video completion status. Use this tool when the CISO asks about their own information or training progress.",
}

GET_ALL_EMPLOYEES_WITH_THIS_TRAINING_STATUS = {
    "type": "function",
    "name": "get_all_employees_with_this_training_status",
    "description": "Get a list of all employees with a specific training status (NOT_STARTED, IN_PROGRESS, or FINISHED). Use this tool when the CISO asks about employees with a particular training status.",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "The training status to filter by: NOT_STARTED, IN_PROGRESS, or FINISHED",
                "enum": ["NOT_STARTED", "IN_PROGRESS", "FINISHED"]
            }
        },
        "required": ["status"]
    }
}

FETCH_DIFFERENT_EMPLOYEE_DATA = {
    "type": "function",
    "name": "fetch_different_employee_data",
    "description": "Fetch any employee's data including personal information and training video completion status. Use this tool when the CISO asks about a specific employee's information or training progress.",
    "parameters": {
        "type": "object",
        "properties": {
            "employee_id": {
                "type": "string",
                "description": "The unique employee ID of the employee to fetch data for"
            },
            "employee_name": {
                "type": "string",
                "description": "The employee's first name only"
            }
        },
        "required": ["employee_id", "employee_name"]
    }
}
