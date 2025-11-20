import sqlite3
from pathlib import Path
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from contextlib import contextmanager

# Get the database path relative to this file
# In Docker: backend/ is mounted to /app, so backend/app/db/queries.py becomes /app/app/db/queries.py
# We need to go up 3 levels: /app/app/db/ -> /app/app/ -> /app/ -> then to data/employees.db
DB_PATH = Path(__file__).parent.parent.parent / "data" / "employees.db"
logger = logging.getLogger("db")

# Constants
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
SECONDS_PER_DAY = 24 * 3600
NUM_VIDEOS = 4

# Training status constants
STATUS_FINISHED = "FINISHED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_NOT_STARTED = "NOT_STARTED"

# Division constants
DIVISION_CISO = "CISO"

# Video column names
VIDEO_NAMES = ["first", "second", "third", "fourth"]
VIDEO_START_COLUMNS = [
    "START_FIRST_VIDEO_DATE",
    "START_SECOND_VIDEO_DATE",
    "START_THIRD_VIDEO_DATE",
    "START_FOURTH_VIDEO_DATE"
]
VIDEO_FINISH_COLUMNS = [
    "FINISH_FIRST_VIDEO_DATE",
    "FINISH_SECOND_VIDEO_DATE",
    "FINISH_THIRD_VIDEO_DATE",
    "FINISH_FOURTH_VIDEO_DATE"
]

# Employee tuple column indices (when using SELECT *)
COL_EMPLOYEE_ID = 0
COL_EMPLOYEE_NAME = 1
COL_EMPLOYEE_LAST_NAME = 2
COL_START_FIRST_VIDEO = 4
COL_FINISH_FIRST_VIDEO = 5
COL_START_SECOND_VIDEO = 6
COL_FINISH_SECOND_VIDEO = 7
COL_START_THIRD_VIDEO = 8
COL_FINISH_THIRD_VIDEO = 9
COL_START_FOURTH_VIDEO = 10
COL_FINISH_FOURTH_VIDEO = 11


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    with sqlite3.connect(DB_PATH) as conn:
        yield conn

def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse a date string to datetime object."""
    if date_str is None:
        return None
    try:
        return datetime.strptime(date_str, DATE_FORMAT)
    except (ValueError, TypeError):
        return None


def _parse_dates(date_strings: List[Optional[str]]) -> List[datetime]:
    """Parse a list of date strings, filtering out None and invalid dates."""
    valid_dates = []
    for date_str in date_strings:
        parsed = _parse_date(date_str)
        if parsed is not None:
            valid_dates.append(parsed)
    return valid_dates


def _days_between_dates(finish_date: Optional[datetime], start_date: Optional[datetime]) -> float:
    """Calculate days between two datetime objects."""
    if finish_date is None or start_date is None:
        return 0.0
    time_delta = finish_date - start_date
    return time_delta.total_seconds() / SECONDS_PER_DAY


def _execute_query(
    query: str,
    params: Optional[Tuple] = None,
    fetch_one: bool = False
) -> Optional[Any]:
    """Execute a database query and return results."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchone() if fetch_one else cursor.fetchall()
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return None


def _get_employee_by_id_and_name(
    employee_id: str,
    employee_name: str,
    additional_where: Optional[str] = None,
    additional_params: Optional[Tuple] = None
) -> Optional[Tuple]:
    """Get employee row by ID and name, with optional additional WHERE conditions."""
    base_query = "SELECT * FROM employees WHERE EMPLOYEE_ID = ? AND EMPLOYEE_NAME = ?"
    params = (employee_id, employee_name)
    
    if additional_where:
        base_query += f" AND {additional_where}"
        if additional_params:
            params = params + additional_params
    
    return _execute_query(base_query, params, fetch_one=True)


def _calculate_training_status_from_finish_dates(finish_dates: List[Optional[str]]) -> str:
    """Calculate training status from a list of finish dates."""
    finished_count = sum(1 for date in finish_dates if date is not None)
    
    if finished_count == 0:
        return STATUS_NOT_STARTED
    elif finished_count == NUM_VIDEOS:
        return STATUS_FINISHED
    else:
        return STATUS_IN_PROGRESS


def _build_status_query(status: str, finish_columns: List[str]) -> str:
    """Build SQL query for fetching employees by training status."""
    if status == STATUS_FINISHED:
        conditions = " AND ".join(f"{col} IS NOT NULL" for col in finish_columns)
        return f"SELECT * FROM employees WHERE {conditions}"
    elif status == STATUS_IN_PROGRESS:
        any_finished = " OR ".join(f"{col} IS NOT NULL" for col in finish_columns)
        all_finished = " AND ".join(f"{col} IS NOT NULL" for col in finish_columns)
        return f"SELECT * FROM employees WHERE ({any_finished}) AND NOT ({all_finished})"
    elif status == STATUS_NOT_STARTED:
        conditions = " AND ".join(f"{col} IS NULL" for col in finish_columns)
        return f"SELECT * FROM employees WHERE {conditions}"
    else:
        logger.warning(f"Unknown status: {status}")
        return "SELECT * FROM employees WHERE 1=0"  # Return empty result


def _build_video_data(result: Tuple, video_names: List[str]) -> Dict[str, Any]:
    """Build video data dictionary from query result tuple."""
    video_data = {}
    for i, video_name in enumerate(video_names):
        start_idx = i * 2
        finish_idx = start_idx + 1
        video_data[f"started_{video_name}_video_time"] = result[start_idx]
        video_data[f"finished_{video_name}_video_time"] = result[finish_idx]
        video_data[f"time_to_finish_{video_name}_video"] = calculate_time_diff(
            result[finish_idx], result[start_idx]
        )
    return video_data


def _extract_employee_info(employee_tuple: Tuple, employee_id: str, employee_name: str) -> Dict[str, Any]:
    """Extract employee information dictionary from employee tuple."""
    return {
        "employee_name": employee_tuple[COL_EMPLOYEE_NAME],
        "employee_last_name": employee_tuple[COL_EMPLOYEE_LAST_NAME],
        "employee_id": employee_tuple[COL_EMPLOYEE_ID]
    }


def _get_video_dates_from_employee_tuple(employee: Tuple) -> Tuple[List[Optional[str]], List[Optional[str]]]:
    """Extract start and finish dates from employee tuple."""
    start_date_indices = [
        COL_START_FIRST_VIDEO,
        COL_START_SECOND_VIDEO,
        COL_START_THIRD_VIDEO,
        COL_START_FOURTH_VIDEO
    ]
    finish_date_indices = [
        COL_FINISH_FIRST_VIDEO,
        COL_FINISH_SECOND_VIDEO,
        COL_FINISH_THIRD_VIDEO,
        COL_FINISH_FOURTH_VIDEO
    ]
    
    start_dates = [employee[idx] for idx in start_date_indices]
    finish_dates = [employee[idx] for idx in finish_date_indices]
    
    return start_dates, finish_dates


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

def calculate_time_diff(finish_date: Optional[str], start_date: Optional[str]) -> float:
    """Calculate the time difference in days between two datetime strings. """
    finish_dt = _parse_date(finish_date)
    start_dt = _parse_date(start_date)
    return _days_between_dates(finish_dt, start_dt)

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

def fetch_all_employees_with_this_training_status(status: str) -> Optional[List[Tuple]]:
    """Fetch all employees with a given training status."""
    query = _build_status_query(status, VIDEO_FINISH_COLUMNS)
    return _execute_query(query, fetch_one=False)

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

def calculate_employee_time_to_finish_training(employee: Tuple) -> float:
    """Calculate the time (in days) it took for an employee to finish all training videos."""
    start_dates, finish_dates = _get_video_dates_from_employee_tuple(employee)
    
    valid_start_dates = _parse_dates(start_dates)
    valid_finish_dates = _parse_dates(finish_dates)
    
    if not valid_start_dates or not valid_finish_dates:
        return 0.0
    
    earliest_start = min(valid_start_dates)
    latest_finish = max(valid_finish_dates)
    
    return _days_between_dates(latest_finish, earliest_start)
    