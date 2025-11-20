from app.db.common import (
    calculate_time_diff,
    _build_status_query,
    STATUS_FINISHED,
    STATUS_IN_PROGRESS,
    STATUS_NOT_STARTED,
)


def test_calculate_time_diff_handles_valid_dates():
    start = "2024-01-01 00:00:00"
    finish = "2024-01-04 00:00:00"
    assert calculate_time_diff(finish, start) == 3.0


def test_build_status_query_for_finished_and_not_started():
    finished_query = _build_status_query(STATUS_FINISHED, ["f1", "f2"])
    in_progress_query = _build_status_query(STATUS_IN_PROGRESS, ["f1", "f2"])
    not_started_query = _build_status_query(STATUS_NOT_STARTED, ["f1", "f2"])

    assert finished_query == "SELECT * FROM employees WHERE f1 IS NOT NULL AND f2 IS NOT NULL"
    assert "f1 IS NOT NULL" in in_progress_query and "NOT (f1 IS NOT NULL AND f2 IS NOT NULL)" in in_progress_query
    assert not_started_query == "SELECT * FROM employees WHERE f1 IS NULL AND f2 IS NULL"
