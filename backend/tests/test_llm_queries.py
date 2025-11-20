import pytest
from types import SimpleNamespace

from app.services.llm import llm_queries, llm_config
from app.services.cache import clear_all_caches


class DummyResponses:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


class DummyClient:
    def __init__(self, responses):
        self.responses = DummyResponses(responses)


def make_response(output=None, output_text=""):
    return SimpleNamespace(output=output or [], output_text=output_text)


@pytest.fixture(autouse=True)
def reset_cache():
    clear_all_caches()
    yield
    clear_all_caches()


@pytest.mark.anyio
async def test_authenticate_employee_handles_existing_user(monkeypatch):
    dummy_client = DummyClient([make_response(output_text="ignored")])
    monkeypatch.setattr(llm_queries, "client", dummy_client)
    
    async def fake_function_call_outputs(*args, **kwargs):
        return ([{llm_config.KEY_OUTPUT: {llm_config.KEY_EXISTS: True}}], "99", "Alice")

    monkeypatch.setattr(llm_queries, "get_function_call_outputs", fake_function_call_outputs)

    result = await llm_queries.authenticate_employee("hello")

    assert result[llm_config.KEY_MESSAGE] == "Hi Alice, how can I help you?"
    assert result[llm_config.KEY_EMPLOYEE_ID] == "99"
    assert dummy_client.responses.calls[0]["model"] == llm_config.MODEL_NAME


@pytest.mark.anyio
async def test_authenticate_employee_handles_missing_user(monkeypatch):
    dummy_client = DummyClient([make_response(output_text="ignored")])
    monkeypatch.setattr(llm_queries, "client", dummy_client)
    
    async def fake_function_call_outputs(*args, **kwargs):
        return ([{llm_config.KEY_OUTPUT: {llm_config.KEY_EXISTS: False}}], None, None)

    monkeypatch.setattr(llm_queries, "get_function_call_outputs", fake_function_call_outputs)

    result = await llm_queries.authenticate_employee("hello")
    assert "wrong name or id" in result[llm_config.KEY_MESSAGE]


@pytest.mark.anyio
async def test_execute_query_with_tools_triggers_follow_up(monkeypatch):
    initial_response = make_response(output=[{llm_config.KEY_TYPE: llm_config.FUNCTION_CALL_TYPE}], output_text="step1")
    followup_response = make_response(output_text="final text")
    dummy_client = DummyClient([followup_response])
    monkeypatch.setattr(llm_queries, "client", dummy_client)

    async def fake_make_initial_request(*args, **kwargs):
        return initial_response, [{"role": "user", "content": "hi"}], [{"call": "output"}], None, None

    monkeypatch.setattr(llm_queries, "_make_initial_request", fake_make_initial_request)

    result = await llm_queries.execute_query_with_tools("hi", [], [], "instruction", 1)

    assert result[llm_config.KEY_MESSAGE] == "final text"
    assert len(dummy_client.responses.calls) == 1
