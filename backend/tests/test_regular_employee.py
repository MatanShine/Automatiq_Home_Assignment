from app.db import regular_employee
from app.db.common import STATUS_FINISHED


def test_fetch_employee_data_returns_structured_payload(monkeypatch):
    sample_result = (
        "2024-01-01 00:00:00", "2024-01-02 00:00:00",
        "2024-01-03 00:00:00", "2024-01-04 00:00:00",
        "2024-01-05 00:00:00", "2024-01-06 00:00:00",
        "2024-01-07 00:00:00", "2024-01-08 00:00:00",
        "Engineering", "Doe"
    )

    def fake_execute(query, params=None, fetch_one=False):
        return sample_result

    def fake_fetch_status(emp_id, emp_name):
        return STATUS_FINISHED

    monkeypatch.setattr(regular_employee, "_execute_query", fake_execute)
    monkeypatch.setattr(regular_employee, "fetch_employee_training_status", fake_fetch_status)

    data = regular_employee.fetch_employee_data("1", "John")

    assert data["personal data"] == {
        "employee_id": "1",
        "employee_name": "John",
        "employee_last_name": "Doe",
        "employee_division": "Engineering",
    }
    assert data["training_status"] == STATUS_FINISHED
    assert data["time_to_finish_first_video"] == 1.0


def test_fetch_employee_training_status(monkeypatch):
    finish_dates = (
        "2024-01-02 00:00:00",
        "2024-01-04 00:00:00",
        "2024-01-06 00:00:00",
        "2024-01-08 00:00:00",
    )

    monkeypatch.setattr(regular_employee, "_execute_query", lambda q, p=None, fetch_one=False: finish_dates)
    status = regular_employee.fetch_employee_training_status("1", "John")
    assert status == STATUS_FINISHED


def test_calculate_employee_time_to_finish_training(monkeypatch):
    employee_tuple = (
        "1", "John", "Doe", "Engineering",
        "2024-01-01 00:00:00", "2024-01-02 00:00:00",
        "2024-01-03 00:00:00", "2024-01-05 00:00:00",
        "2024-01-06 00:00:00", "2024-01-07 00:00:00",
        "2024-01-08 00:00:00", "2024-01-09 00:00:00",
    )

    total_days = regular_employee.calculate_employee_time_to_finish_training(employee_tuple)
    assert total_days == 8.0
