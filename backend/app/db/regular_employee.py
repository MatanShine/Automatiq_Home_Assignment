"""Functions for regular employee data operations."""
from typing import Optional, Dict, Any
from app.db.common import (
    _execute_query,
    _build_video_data,
    _calculate_training_status_from_finish_dates,
    _parse_dates,
    _get_video_dates_from_employee_tuple,
    _days_between_dates,
    calculate_time_diff,
    VIDEO_NAMES,
    VIDEO_START_COLUMNS,
    VIDEO_FINISH_COLUMNS,
    NUM_VIDEOS,
    logger
)


def fetch_employee_data(employee_id: str, employee_name: str) -> Optional[Dict[str, Any]]:
    """Fetch employee personal data and video completion status from the database by ID and name."""
    columns = ", ".join(VIDEO_START_COLUMNS[i] + ", " + VIDEO_FINISH_COLUMNS[i] for i in range(NUM_VIDEOS))
    columns += ", EMPLOYEE_DIVISION, EMPLOYEE_LAST_NAME"
    
    query = f"SELECT {columns} FROM employees WHERE EMPLOYEE_ID = ? AND EMPLOYEE_NAME = ?"
    result = _execute_query(query, (employee_id, employee_name), fetch_one=True)
    
    if result is None:
        logger.warning(f"Employee not found: ID={employee_id}, Name={employee_name}")
        return None
    
    video_data = _build_video_data(result, VIDEO_NAMES)
    
    # Last two columns are division and last_name
    division_idx = NUM_VIDEOS * 2
    last_name_idx = division_idx + 1
    
    return {
        "personal data": {
            "employee_id": employee_id,
            "employee_name": employee_name,
            "employee_last_name": result[last_name_idx],
            "employee_division": result[division_idx]
        },
        **video_data,
        "training_status": fetch_employee_training_status(employee_id, employee_name)
    }


def fetch_employee_training_status(employee_id: str, employee_name: str) -> Optional[str]:
    """Fetch the training status of an employee."""
    columns = ", ".join(VIDEO_FINISH_COLUMNS)
    query = f"SELECT {columns} FROM employees WHERE EMPLOYEE_ID = ? AND EMPLOYEE_NAME = ?"
    result = _execute_query(query, (employee_id, employee_name), fetch_one=True)
    
    if result is None:
        logger.warning(f"Employee not found for training status: ID={employee_id}, Name={employee_name}")
        return None

    finish_dates = list(result[:NUM_VIDEOS])
    return _calculate_training_status_from_finish_dates(finish_dates)


def calculate_employee_time_to_finish_training(employee) -> float:
    """Calculate the time (in days) it took for an employee to finish all training videos."""
    start_dates, finish_dates = _get_video_dates_from_employee_tuple(employee)
    
    valid_start_dates = _parse_dates(start_dates)
    valid_finish_dates = _parse_dates(finish_dates)
    
    if not valid_start_dates or not valid_finish_dates:
        return 0.0
    
    earliest_start = min(valid_start_dates)
    latest_finish = max(valid_finish_dates)
    
    return _days_between_dates(latest_finish, earliest_start)

