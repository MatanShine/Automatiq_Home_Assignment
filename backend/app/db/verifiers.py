"""Verification functions for checking employee existence and validity."""
from app.db.common import _execute_query
from app.db.common import _get_employee_by_id_and_name, DIVISION_CISO


def employee_exists_in_database(employee_id: str, employee_name: str) -> bool:
    """Check if an employee exists in the database by ID and name."""
    result = _execute_query(
        "SELECT 1 FROM employees WHERE EMPLOYEE_ID = ? AND EMPLOYEE_NAME = ?",
        (employee_id, employee_name),
        fetch_one=True
    )
    return result is not None

def is_ciso(employee_id: str, employee_name: str) -> bool:
    """Check if an employee is a CISO."""
    result = _get_employee_by_id_and_name(
        employee_id,
        employee_name,
        additional_where="EMPLOYEE_DIVISION = ?",
        additional_params=(DIVISION_CISO,)
    )
    return result is not None

