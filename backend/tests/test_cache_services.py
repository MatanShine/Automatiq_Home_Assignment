import asyncio
import pytest

from app.services.cache import cache_analytics, cache_llm, clear_all_caches


@pytest.fixture(autouse=True)
def clear_caches():
    clear_all_caches()
    yield
    clear_all_caches()


def test_cache_analytics_decorator_caches_result():
    calls = []

    @cache_analytics
    def expensive_add(a, b):
        calls.append((a, b))
        return a + b

    first = expensive_add(1, 2)
    second = expensive_add(1, 2)

    assert first == 3
    assert second == 3
    assert calls == [(1, 2)]


@pytest.mark.anyio
async def test_cache_llm_decorator_caches_async_calls():
    calls = []

    @cache_llm
    async def async_query(user_message, history=None, employee_id=None, employee_name=None):
        calls.append((user_message, employee_id, employee_name))
        return {"message": user_message, "employee_id": employee_id, "employee_name": employee_name}

    first = await async_query("hello", employee_id="42", employee_name="Alice")
    second = await async_query("hello", employee_id="42", employee_name="Alice")

    assert first == {"message": "hello", "employee_id": "42", "employee_name": "Alice"}
    assert second == first
    assert calls == [("hello", "42", "Alice")]
