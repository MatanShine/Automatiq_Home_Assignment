import sqlite3
from pathlib import Path

# Get the database path relative to this file
# In Docker: backend/ is mounted to /app, so backend/app/db/queries.py becomes /app/app/db/queries.py
# We need to go up 3 levels: /app/app/db/ -> /app/app/ -> /app/ -> then to data/employees.db
DB_PATH = Path(__file__).parent.parent.parent / "data" / "employees.db"


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
                "SELECT COUNT(*) FROM employees WHERE EMPLOYEE_ID = ? AND EMPLOYEE_NAME = ? COLLATE NOCASE",
                (employee_id, employee_name)
            )
            result = cursor.fetchone()
            return result[0] > 0 if result else False
    except Exception as e:
        # Log error in production, for now just return False
        print(f"Error checking employee in database: {e}")
        return False

