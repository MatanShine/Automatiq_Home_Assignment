"""
Data formatting utilities for LLM client.
"""
import json
from typing import Any, Dict, List, Optional


def format_json_output(data: Any, error_message: str) -> str:
    """Format data as JSON string with error handling."""
    if data:
        return json.dumps(data)
    return json.dumps({"error": error_message})


def format_employee_data_output(employee_data: Optional[Dict[str, Any]], error_message: str = "Employee data not found") -> str:
    """Format employee data as JSON string with error handling."""
    return format_json_output(employee_data, error_message)


def format_employees_by_status(employees: List[Any]) -> Dict[str, Any]:
    """Format employee list with status into structured format."""
    if not employees:
        return {"error": "No employees found with this status", "employees": [], "count": 0}
    
    formatted_employees = [
        {
            "employee_id": emp[0],
            "employee_name": emp[1],
            "employee_last_name": emp[2],
            "employee_division": emp[3] if len(emp) > 3 else None
        }
        for emp in employees
    ]
    return {"employees": formatted_employees, "count": len(formatted_employees)}

