"""
Main query execution functions for LLM client.
"""
from typing import Optional, List, Dict, Any, Tuple
from app.services.llm_client_setup import client, logger
from app.services.llm_config import (
    MODEL_NAME,
    INSTRUCTION_AUTHENTICATE,
    INSTRUCTION_TRAINING_ASSISTANT,
    KEY_EXISTS, KEY_OUTPUT
)
from app.services.llm_responses import (
    create_response,
    create_error_response,
    extract_output_text,
    build_messages_with_function_calls,
    build_prompt
)
from app.services.llm_tool_handlers import get_function_call_outputs
from app.services.tools import (
    CHECK_IF_EMPLOYEE_EXISTS_BY_ID_AND_NAME,
    FETCH_CURRENT_EMPLOYEE_DATA,
    FETCH_CURRENT_EMPLOYEE_TRAINING_STATUS,
    GET_STATISTIC_SUMMARY_ON_TRAINING,
    FETCH_CURRENT_CISO_EMPLOYEE_DATA,
    GET_ALL_EMPLOYEES_WITH_THIS_TRAINING_STATUS,
    FETCH_DIFFERENT_EMPLOYEE_DATA
)


async def _make_initial_request(
    user_message: str,
    history: Optional[List[Dict[str, Any]]],
    tools: List[Any],
    instructions: str,
    max_tool_calls: int,
    employee_id: Optional[str] = None,
    employee_name: Optional[str] = None
) -> Tuple[Any, List[Dict[str, Any]], List[Dict[str, Any]], Optional[str], Optional[str]]:
    """Make initial API request and process function calls."""
    messages = build_prompt(user_message, history)
    response = await client.responses.create(
        model=MODEL_NAME,
        input=messages,
        instructions=instructions,
        tools=tools,
        max_tool_calls=max_tool_calls
    )
    function_call_outputs, extracted_employee_id, extracted_employee_name = await get_function_call_outputs(
        response.output,
        current_employee_id=employee_id,
        current_employee_name=employee_name
    )
    logger.info(f"Function call outputs: {function_call_outputs}")

    return response, messages, function_call_outputs, extracted_employee_id, extracted_employee_name


async def execute_query_with_tools(
    user_message: str,
    history: Optional[List[Dict[str, Any]]],
    tools: List[Any],
    instructions: str,
    max_tool_calls: int,
    employee_id: Optional[str] = None,
    employee_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generic function to execute a query with tools.
    Handles the common pattern of: make request -> process function calls -> make final request.
    """
    try:
        response, messages, function_call_outputs, _, _ = await _make_initial_request(
            user_message, history, tools, instructions, max_tool_calls, employee_id, employee_name
        )
        if function_call_outputs:
            messages_with_outputs = build_messages_with_function_calls(messages, response.output, function_call_outputs)
            logger.info(f"Messages with outputs: {function_call_outputs}")
            response = await client.responses.create(
                model=MODEL_NAME,
                input=messages_with_outputs,
                instructions=instructions,
            )
        return create_response(extract_output_text(response), employee_id, employee_name)
    except Exception as e:
        return create_error_response(e, employee_id, employee_name)


async def authenticate_employee(
    user_message: str,
    history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Query OpenAI Responses API with authentication tools.
    """
    try:
        response, _, function_call_outputs, extracted_employee_id, extracted_employee_name = await _make_initial_request(
            user_message=user_message,
            history=history,
            tools=[CHECK_IF_EMPLOYEE_EXISTS_BY_ID_AND_NAME],
            instructions=INSTRUCTION_AUTHENTICATE,
            max_tool_calls=1
        )
        if not function_call_outputs:
            return create_response(extract_output_text(response))
        exists = function_call_outputs[0].get(KEY_OUTPUT, {}).get(KEY_EXISTS, False)
        if not exists:
            return create_response(
                "You gave me the wrong name or id, or the user does not exist in the database. Please try again."
            )
        return create_response(
            f"Hi {extracted_employee_name}, how can I help you?",
            extracted_employee_id,
            extracted_employee_name
        )
    except Exception as e:
        return create_error_response(e)


async def ciso_query(
    user_message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    employee_id: Optional[str] = None,
    employee_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query OpenAI Responses API with ciso tools.
    """
    instructions = INSTRUCTION_TRAINING_ASSISTANT.format(user_type="the ciso")
    return await execute_query_with_tools(
        user_message=user_message,
        history=history,
        tools=[GET_STATISTIC_SUMMARY_ON_TRAINING, FETCH_CURRENT_CISO_EMPLOYEE_DATA, GET_ALL_EMPLOYEES_WITH_THIS_TRAINING_STATUS, FETCH_DIFFERENT_EMPLOYEE_DATA],
        instructions=instructions,
        max_tool_calls=3,
        employee_id=employee_id,
        employee_name=employee_name
    )


async def regular_employee_query(
    user_message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    employee_id: Optional[str] = None,
    employee_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query OpenAI Responses API with regular employee tools.
    """
    instructions = INSTRUCTION_TRAINING_ASSISTANT.format(user_type="an employee")
    return await execute_query_with_tools(
        user_message=user_message,
        history=history,
        tools=[FETCH_CURRENT_EMPLOYEE_DATA, FETCH_CURRENT_EMPLOYEE_TRAINING_STATUS],
        instructions=instructions,
        max_tool_calls=1,
        employee_id=employee_id,
        employee_name=employee_name
    )

