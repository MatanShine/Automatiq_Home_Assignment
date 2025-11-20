"""
Response utilities for LLM client.
"""
from typing import Optional, List, Dict, Any, TypedDict
from app.services.llm.llm_config import (
    KEY_MESSAGE, KEY_EMPLOYEE_ID, KEY_EMPLOYEE_NAME,
    EMPTY_RESPONSE_MESSAGE, ERROR_MESSAGE_PREFIX,
    FUNCTION_CALL_TYPE, FUNCTION_CALL_OUTPUT_TYPE,
    KEY_TYPE, KEY_CALL_ID, KEY_OUTPUT
)
from app.services.llm.llm_client_setup import logger


class QueryResponse(TypedDict):
    message: str
    employee_id: Optional[str]
    employee_name: Optional[str]


def create_response(message: str, employee_id: Optional[str] = None, employee_name: Optional[str] = None) -> QueryResponse:
    """Create a standardized response dictionary."""
    return {
        KEY_MESSAGE: message,
        KEY_EMPLOYEE_ID: employee_id,
        KEY_EMPLOYEE_NAME: employee_name
    }


def create_error_response(error: Exception, employee_id: Optional[str] = None, employee_name: Optional[str] = None) -> QueryResponse:
    """Create an error response dictionary."""
    logger.error(f"Error in query execution: {error}")
    return create_response(f"{ERROR_MESSAGE_PREFIX} {str(error)}", employee_id, employee_name)


def extract_output_text(response: Any) -> str:
    """Extract output text from response, with fallback."""
    return (getattr(response, "output_text", None) or "").strip() or EMPTY_RESPONSE_MESSAGE


def build_messages_with_function_calls(messages: List[Dict[str, Any]], response_output: List[Any], function_call_outputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build messages list with function calls and their outputs."""
    messages_with_outputs = messages.copy()
    for item in response_output or []:
        if getattr(item, KEY_TYPE, None) == FUNCTION_CALL_TYPE:
            messages_with_outputs.append(item)
    messages_with_outputs.extend(function_call_outputs)
    return messages_with_outputs


def create_function_call_output(call_id: str, output: Any) -> Dict[str, Any]:
    """Create a standardized function call output dictionary."""
    return {
        KEY_TYPE: FUNCTION_CALL_OUTPUT_TYPE,
        KEY_CALL_ID: call_id,
        KEY_OUTPUT: output
    }


def build_prompt(user_message: str, history: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Build messages list from history and current user message."""
    history = history or []
    messages: List[Dict[str, Any]] = []

    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})
    return messages

