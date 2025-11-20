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


def calculate_time_diff(finish_date: Optional[str], start_date: Optional[str]) -> float:
    """Calculate the time difference in days between two datetime strings."""
    finish_dt = _parse_date(finish_date)
    start_dt = _parse_date(start_date)
    return _days_between_dates(finish_dt, start_dt)


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

