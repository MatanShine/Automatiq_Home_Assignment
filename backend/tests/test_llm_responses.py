from types import SimpleNamespace

from app.services.llm import llm_responses
from app.services.llm import llm_config


def test_create_error_response_includes_prefix():
    error = ValueError("boom")
    response = llm_responses.create_error_response(error, employee_id="1", employee_name="John")
    assert response[llm_config.KEY_MESSAGE].startswith(llm_config.ERROR_MESSAGE_PREFIX)
    assert response[llm_config.KEY_EMPLOYEE_ID] == "1"


def test_extract_output_text_with_missing_value():
    resp = SimpleNamespace(output_text="  Hello world  ")
    assert llm_responses.extract_output_text(resp) == "Hello world"
    assert llm_responses.extract_output_text(SimpleNamespace()) == llm_config.EMPTY_RESPONSE_MESSAGE


def test_build_messages_with_function_calls_appends_outputs():
    function_call_item = {llm_config.KEY_TYPE: llm_config.FUNCTION_CALL_TYPE, "content": "call"}
    messages = [{"role": "user", "content": "hi"}]
    result = llm_responses.build_messages_with_function_calls(messages, [function_call_item], [{"result": "ok"}])
    assert result[0] == messages[0]
    assert result[-1] == {"result": "ok"}


def test_build_prompt_includes_history():
    history = [{"role": "assistant", "content": "previous"}]
    messages = llm_responses.build_prompt("new message", history)
    assert messages[0] == {"role": "assistant", "content": "previous"}
    assert messages[-1]["content"] == "new message"
