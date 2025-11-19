import sqlite3

DB_PATH = "backend/data/employees.db"

def fetch_employees(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT EMPLOYEE_ID, EMPLOYEE_NAME, EMPLOYEE_LAST_NAME FROM employees")
    return cursor.fetchall()
def fetch_employee_divisions(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT EMPLOYEE_DIVISION FROM employees")
    return cursor.fetchall()
def fetch_ciso(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE EMPLOYEE_DIVISION = 'CISO'")
    return cursor.fetchall()
def fetch_columns(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(employees)")
    return cursor.fetchall()
def fetch_employee_videos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT START_FIRST_VIDEO_DATE, FINISH_FIRST_VIDEO_DATE, START_SECOND_VIDEO_DATE, FINISH_SECOND_VIDEO_DATE, START_THIRD_VIDEO_DATE, FINISH_THIRD_VIDEO_DATE, START_FOURTH_VIDEO_DATE, FINISH_FOURTH_VIDEO_DATE FROM employees")
    return cursor.fetchall()

def main():
    with sqlite3.connect(DB_PATH) as conn:
        employees = fetch_employees(conn)
        columns = fetch_columns(conn)
        employee_divisions = fetch_employee_divisions(conn)
        ciso = fetch_ciso(conn)
        print("Employees:")
        print(employees)
        print("Columns:")
        print(columns)
        print("Employee Divisions:")
        print(employee_divisions)
        print("CISO:")
        print(ciso)
        print("first 3 employees videos:")
        print(fetch_employee_videos(conn)[0:3])
if __name__ == "__main__":
    main()