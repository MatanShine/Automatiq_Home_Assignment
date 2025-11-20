from app.db import ciso
from app.db.common import STATUS_FINISHED, STATUS_IN_PROGRESS, STATUS_NOT_STARTED


def make_employee(emp_id, first_name, last_name, duration_days):
    # start and finish dates with given duration
    start = "2024-01-01 00:00:00"
    finish = f"2024-01-{1 + duration_days:02d} 00:00:00"
    return (
        emp_id, first_name, last_name, "Division",
        start, finish,
        start, finish,
        start, finish,
        start, finish,
    )


def test_fetch_all_employees_with_status(monkeypatch):
    expected_query = "expected"

    def fake_build(status, finish_cols):
        return expected_query + status

    def fake_execute(query, params=None, fetch_one=False):
        return [(1, 2, 3)] if query.startswith(expected_query) else []

    monkeypatch.setattr(ciso, "_build_status_query", fake_build)
    monkeypatch.setattr(ciso, "_execute_query", fake_execute)

    result = ciso.fetch_all_employees_with_this_training_status(STATUS_FINISHED)
    assert result == [(1, 2, 3)]


def test_calculate_time_to_finish_training(monkeypatch):
    finished = [make_employee("1", "Fast", "Employee", 2), make_employee("2", "Slow", "Employee", 6)]
    in_progress = [make_employee("3", "Mid", "Employee", 3)]
    not_started = []

    stats = ciso.calculate_time_to_finish_training(finished, in_progress, not_started)

    assert stats["amount_of_finished_employees"] == 2
    assert stats["average_time_to_finish_training"] == (2.0 + 6.0) / 2
    assert stats["fastest_employee_to_finish_training"]["employee_name"] == "Fast"
    assert stats["slowest_employee_to_finish_training"]["employee_name"] == "Slow"
