"""CISO-specific functions for analytics and statistics."""
from typing import Optional, List, Dict, Any, Tuple
from app.services.cache.db_cache import cache_analytics
from app.db.common import (
    _execute_query,
    _build_status_query,
    _extract_employee_info,
    VIDEO_FINISH_COLUMNS,
    STATUS_FINISHED,
    STATUS_IN_PROGRESS,
    STATUS_NOT_STARTED,
    COL_EMPLOYEE_ID,
    COL_EMPLOYEE_NAME
)
from app.db.regular_employee import calculate_employee_time_to_finish_training


@cache_analytics
def fetch_all_employees_with_this_training_status(status: str) -> Optional[List[Tuple]]:
    """Fetch all employees with a given training status."""
    query = _build_status_query(status, VIDEO_FINISH_COLUMNS)
    return _execute_query(query, fetch_one=False)


@cache_analytics
def get_statistic_summary() -> Dict[str, Any]:
    """Get a summary of training statistics."""
    finished_employees = fetch_all_employees_with_this_training_status(STATUS_FINISHED) or []
    in_progress_employees = fetch_all_employees_with_this_training_status(STATUS_IN_PROGRESS) or []
    not_started_employees = fetch_all_employees_with_this_training_status(STATUS_NOT_STARTED) or []
    return calculate_time_to_finish_training(finished_employees, in_progress_employees, not_started_employees)


def calculate_time_to_finish_training(
    finished_employees: List[Tuple],
    in_progress_employees: List[Tuple],
    not_started_employees: List[Tuple]
) -> Dict[str, Any]:
    """Calculate training time statistics."""
    if not finished_employees:
        empty_employee = {"employee_name": None, "employee_last_name": None, "employee_id": None}
        return {
            "amount_of_finished_employees": 0,
            "amount_of_in_progress_employees": len(in_progress_employees),
            "amount_of_not_started_employees": len(not_started_employees),
            "minimum_time": 0.0,
            "fastest_employee": empty_employee.copy(),
            "maximum_time": 0.0,
            "slowest_employee": empty_employee.copy(),
            "average_time": 0.0,
        }
    
    times = [calculate_employee_time_to_finish_training(emp) for emp in finished_employees]
    minimum_time = min(times)
    maximum_time = max(times)
    average_time = sum(times) / len(times)
    
    fastest_idx = times.index(minimum_time)
    slowest_idx = times.index(maximum_time)
    fastest_emp = finished_employees[fastest_idx]
    slowest_emp = finished_employees[slowest_idx]
    
    return {
        "amount_of_finished_employees": len(finished_employees),
        "amount_of_in_progress_employees": len(in_progress_employees),
        "amount_of_not_started_employees": len(not_started_employees),
        "minimum_time_to_finish_training": minimum_time,
        "fastest_employee_to_finish_training": _extract_employee_info(fastest_emp, fastest_emp[COL_EMPLOYEE_ID], fastest_emp[COL_EMPLOYEE_NAME]),
        "maximum_time_to_finish_training": maximum_time,
        "slowest_employee_to_finish_training": _extract_employee_info(slowest_emp, slowest_emp[COL_EMPLOYEE_ID], slowest_emp[COL_EMPLOYEE_NAME]),
        "average_time_to_finish_training": average_time,
    }

