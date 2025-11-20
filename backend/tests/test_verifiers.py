from app.db import verifiers


def test_employee_exists_in_database(monkeypatch):
    monkeypatch.setattr(verifiers, "_execute_query", lambda q, p=None, fetch_one=False: (1,))
    assert verifiers.employee_exists_in_database("1", "John") is True


def test_is_ciso(monkeypatch):
    monkeypatch.setattr(verifiers, "_get_employee_by_id_and_name", lambda *args, **kwargs: (1,))
    assert verifiers.is_ciso("1", "John") is True
