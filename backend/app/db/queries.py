import sqlite3
from pathlib import Path
import logging
from datetime import datetime
# Get the database path relative to this file
# In Docker: backend/ is mounted to /app, so backend/app/db/queries.py becomes /app/app/db/queries.py
# We need to go up 3 levels: /app/app/db/ -> /app/app/ -> /app/ -> then to data/employees.db
DB_PATH = Path(__file__).parent.parent.parent / "data" / "employees.db"
logger = logging.getLogger("db")


def employee_exists_in_database(employee_id: str, employee_name: str) -> bool:
    """
    Check if an employee exists in the database by ID and name.
    
    Args:
        employee_id: The employee ID to check
        employee_name: The employee name to check
        
    Returns:
        True if employee exists, False otherwise
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM employees WHERE EMPLOYEE_ID = ? AND EMPLOYEE_NAME = ?",
                (employee_id, employee_name)
            )
            result = cursor.fetchone()
            return result[0] > 0 if result else False
    except Exception as e:
        # Log error in production, for now just return False
        logger.error(f"Error checking employee in database: {e}")
        return False

def is_ciso(employee_id: str, employee_name: str) -> bool:
    """
    Check if an employee is a CISO.
    
    Args:
        employee_id: The employee ID to check
        
    Returns:
        True if employee is a CISO, False otherwise
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees WHERE EMPLOYEE_ID = ? AND EMPLOYEE_NAME = ? AND EMPLOYEE_DIVISION = 'CISO'", (employee_id, employee_name))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        # Log error in production, for now just return False
        logger.error(f"Error checking if employee is a CISO: {e}")
        return False

def fetch_employee_data(employee_id: str, employee_name: str) -> dict:
    """
    Fetch employee data from the database by ID and name.
    
    Args:
        employee_id: The employee ID to fetch
        employee_name: The employee name to fetch
        
    Returns:
        Employee data as a dictionary
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT START_FIRST_VIDEO_DATE, FINISH_FIRST_VIDEO_DATE, START_SECOND_VIDEO_DATE, FINISH_SECOND_VIDEO_DATE, START_THIRD_VIDEO_DATE, FINISH_THIRD_VIDEO_DATE, START_FOURTH_VIDEO_DATE, FINISH_FOURTH_VIDEO_DATE, EMPLOYEE_DIVISION, EMPLOYEE_LAST_NAME FROM employees WHERE EMPLOYEE_ID = ? AND EMPLOYEE_NAME = ?", (employee_id, employee_name))
            result = cursor.fetchone()
            # todo: handle data to 
            return {
                "personal data": {
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "employee_last_name": result[9],
                    "employee_division": result[8]
                },
                "finished_first_video": ("yes" if result[1] is not None else "no"),
                "finished_first_video_date": result[1],
                "finished_second_video": ("yes" if result[3] is not None else "no"),
                "finished_second_video_date": result[3],
                "finished_third_video": ("yes" if result[5] is not None else "no"),
                "finished_third_video_date": result[5],
                "finished_fourth_video": ("yes" if result[7] is not None else "no"),
                "finished_fourth_video_date": result[7],
                "training_status": fetch_employee_training_status(employee_id, employee_name)
            }
    except Exception as e:
        # Log error in production, for now just return None
        logger.error(f"Error fetching employee data: {e}")
        return None

def fetch_employee_training_status(employee_id: str, employee_name: str) -> dict:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT FINISH_FIRST_VIDEO_DATE, FINISH_SECOND_VIDEO_DATE, FINISH_THIRD_VIDEO_DATE, FINISH_FOURTH_VIDEO_DATE FROM employees WHERE EMPLOYEE_ID = ? AND EMPLOYEE_NAME = ?", (employee_id, employee_name))
            result = cursor.fetchone()
            finished_videos = [1 if date is not None else 0 for date in result[:4]]
            if 1 in finished_videos:
                if 0 not in finished_videos:
                    return "FINISHED"
                else:
                    return "IN_PROGRESS"
            else:
                return "NOT_STARTED"
    except Exception as e:
        # Log error in production, for now just return None
        logger.error(f"Error fetching employee training status: {e}")
        return None

def fetch_all_employees_with_this_training_status(status: str) -> list:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if status == "FINISHED":
                cursor.execute("SELECT * FROM employees WHERE FINISH_FIRST_VIDEO_DATE IS NOT NULL AND FINISH_SECOND_VIDEO_DATE IS NOT NULL AND FINISH_THIRD_VIDEO_DATE IS NOT NULL AND FINISH_FOURTH_VIDEO_DATE IS NOT NULL")
            elif status == "IN_PROGRESS":
                cursor.execute("""SELECT * FROM employees 
                                  WHERE (FINISH_FIRST_VIDEO_DATE IS NOT NULL OR FINISH_SECOND_VIDEO_DATE IS NOT NULL OR FINISH_THIRD_VIDEO_DATE IS NOT NULL OR FINISH_FOURTH_VIDEO_DATE IS NOT NULL)
                                  AND NOT (FINISH_FIRST_VIDEO_DATE IS NOT NULL AND FINISH_SECOND_VIDEO_DATE IS NOT NULL AND FINISH_THIRD_VIDEO_DATE IS NOT NULL AND FINISH_FOURTH_VIDEO_DATE IS NOT NULL)
                               """)
            elif status == "NOT_STARTED":
                cursor.execute("SELECT * FROM employees WHERE FINISH_FIRST_VIDEO_DATE IS NULL AND FINISH_SECOND_VIDEO_DATE IS NULL AND FINISH_THIRD_VIDEO_DATE IS NULL AND FINISH_FOURTH_VIDEO_DATE IS NULL")
            result = cursor.fetchall()
            return result
    except Exception as e:
        # Log error in production, for now just return None
        logger.error(f"Error fetching all employees with status: {e}")
        return None

def get_statistic_summary() -> dict:
    finished_employees = fetch_all_employees_with_this_training_status("FINISHED")
    in_progress_employees = fetch_all_employees_with_this_training_status("IN_PROGRESS")
    not_started_employees = fetch_all_employees_with_this_training_status("NOT_STARTED")
    return calculate_time_to_finish_training(finished_employees, in_progress_employees, not_started_employees)

def calculate_time_to_finish_training(finished_employees: list, in_progress_employees: list, not_started_employees: list) -> dict:
    minimum_time = float('inf')
    fastest_employee_name = None
    fastest_employee_last_name = None
    fastest_employee_id = None
    maximum_time = float('-inf')  # Use negative infinity so any positive value will be greater
    slowest_employee_name = None
    slowest_employee_last_name = None
    slowest_employee_id = None
    average_time = 0
    if len(finished_employees) == 0:
        # Handle case when no employees have finished training
        minimum_time = 0.0
        maximum_time = 0.0
        average_time = 0.0
    else:
        for employee in finished_employees:
            time_to_finish = calculate_employee_time_to_finish_training(employee)
            average_time += time_to_finish
            if time_to_finish < minimum_time:
                minimum_time = time_to_finish
                fastest_employee_id = employee[0]
                fastest_employee_name = employee[1]
                fastest_employee_last_name = employee[2]
            if time_to_finish > maximum_time:
                maximum_time = time_to_finish
                slowest_employee_id = employee[0]
                slowest_employee_name = employee[1]
                slowest_employee_last_name = employee[2]
        average_time /= len(finished_employees)
        
        # Convert minimum_time and maximum_time from infinity to 0.0 if they weren't updated
        if minimum_time == float('inf'):
            minimum_time = 0.0
        if maximum_time == float('-inf'):
            maximum_time = 0.0
    return {
        "amount_of_finished_employees": len(finished_employees),
        "amount_of_in_progress_employees": len(in_progress_employees),
        "amount_of_not_started_employees": len(not_started_employees),
        "minimum_time": minimum_time,
        "fastest_employee": {
            "employee_name": fastest_employee_name,
            "employee_last_name": fastest_employee_last_name,
            "employee_id": fastest_employee_id
        },
        "maximum_time": maximum_time,
        "slowest_employee": {
            "employee_name": slowest_employee_name,
            "employee_last_name": slowest_employee_last_name,
            "employee_id": slowest_employee_id
        },
        "average_time": average_time,
    }

def calculate_employee_time_to_finish_training(employee: tuple) -> float:
        """
        Calculate the time (in days) it took for an employee to finish all training videos.
        This is calculated as the time from the earliest start date to the latest finish date.
        
        Args:
            employee: A tuple representing an employee row from the database
            
        Returns:
            Number of days (float) from start to finish of training, or 0 if calculation fails
        """
        # Get start dates: columns 4, 6, 8, 10 (START_FIRST, START_SECOND, START_THIRD, START_FOURTH_VIDEO_DATE)
        start_dates = [employee[4], employee[6], employee[8], employee[10]]
        # Get finish dates: columns 5, 7, 9, 11 (FINISH_FIRST, FINISH_SECOND, FINISH_THIRD, FINISH_FOURTH_VIDEO_DATE)
        finish_dates = [employee[5], employee[7], employee[9], employee[11]]
        
        # Filter out None values and parse dates
        valid_start_dates = []
        for date_str in start_dates:
            if date_str is not None:
                try:
                    # Parse 'YYYY-MM-DD HH:MM:SS' format (TIMESTAMP format)
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    valid_start_dates.append(date_obj)
                except (ValueError, TypeError):
                    continue
        
        valid_finish_dates = []
        for date_str in finish_dates:
            if date_str is not None:
                try:
                    # Parse 'YYYY-MM-DD HH:MM:SS' format (TIMESTAMP format)
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    valid_finish_dates.append(date_obj)
                except (ValueError, TypeError):
                    continue
        
        # For finished employees, we need at least one start and one finish date
        if not valid_start_dates or not valid_finish_dates:
            return 0.0
        
        # Find earliest start date and latest finish date
        earliest_start = min(valid_start_dates)
        latest_finish = max(valid_finish_dates)
        
        # Calculate difference in days
        time_delta = latest_finish - earliest_start
        return time_delta.total_seconds() / (24 * 3600)  # Convert to days
    