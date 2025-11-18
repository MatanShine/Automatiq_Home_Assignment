import sqlite3

DB_PATH = "backend/data/employees.db"

def fetch_employees(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    return cursor.fetchall()

def fetch_columns(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(employees)")
    return cursor.fetchall()

def main():
    with sqlite3.connect(DB_PATH) as conn:
        employees = fetch_employees(conn)
        columns = fetch_columns(conn)
        print("Employees:")
        print(employees)
        print("Columns:")
        print(columns)

if __name__ == "__main__":
    main()