"""
Tool handler functions for processing LLM tool calls.
"""
import json
from typing import Optional, List, Dict, Any, Tuple, Callable
from app.db.queries import (
    employee_exists_in_database,
    fetch_employee_data,
    fetch_employee_training_status,
    get_statistic_summary,
    fetch_all_employees_with_this_training_status
)
from app.services.llm.llm_config import (
    KEY_EMPLOYEE_ID, KEY_EMPLOYEE_NAME, KEY_EXISTS, KEY_OUTPUT,
    FUNCTION_CALL_TYPE, KEY_TYPE
)
from app.services.llm.llm_formatters import (
    format_employee_data_output,
    format_employees_by_status,
    format_json_output
)
from app.services.llm.llm_responses import create_function_call_output
from app.services.llm.llm_client_setup import logger


# Tool handler functions
def _handle_check_employee_exists(arguments: Dict[str, Any], current_employee_id: Optional[str], current_employee_name: Optional[str]) -> Tuple[Any, Optional[str], Optional[str]]:
    """Handle check_if_employee_exists_by_id_and_first_name tool."""
    employee_id = arguments.get(KEY_EMPLOYEE_ID)
    employee_name = arguments.get(KEY_EMPLOYEE_NAME)
    exists = employee_exists_in_database(employee_id, employee_name)
    return {KEY_EXISTS: exists}, employee_id, employee_name


def _handle_fetch_current_user_data(arguments: Dict[str, Any], current_employee_id: Optional[str], current_employee_name: Optional[str]) -> Tuple[Any, Optional[str], Optional[str]]:
    """Handle fetch_current_user_personal_data_and_watched_videos_data tool."""
    employee_data = fetch_employee_data(current_employee_id, current_employee_name)
    return format_employee_data_output(employee_data), None, None


def _handle_fetch_ciso_data(arguments: Dict[str, Any], current_employee_id: Optional[str], current_employee_name: Optional[str]) -> Tuple[Any, Optional[str], Optional[str]]:
    """Handle fetch_current_ciso_employee_data tool."""
    employee_data = fetch_employee_data(current_employee_id, current_employee_name)
    return format_employee_data_output(employee_data), None, None


def _handle_fetch_training_status(arguments: Dict[str, Any], current_employee_id: Optional[str], current_employee_name: Optional[str]) -> Tuple[Any, Optional[str], Optional[str]]:
    """Handle fetch_current_employee_training_status tool."""
    training_status = fetch_employee_training_status(current_employee_id, current_employee_name)
    return format_json_output({"training_status": training_status}, "Training status not found"), None, None


def _handle_get_statistics(arguments: Dict[str, Any], current_employee_id: Optional[str], current_employee_name: Optional[str]) -> Tuple[Any, Optional[str], Optional[str]]:
    """Handle get_summary_and_statistics_on_all_employees_training tool."""
    statistics = get_statistic_summary()
    return format_json_output(statistics, "Statistics not available"), None, None


def _handle_get_employees_by_status(arguments: Dict[str, Any], current_employee_id: Optional[str], current_employee_name: Optional[str]) -> Tuple[Any, Optional[str], Optional[str]]:
    """Handle get_all_employees_with_this_training_status tool."""
    status = arguments.get("status")
    employees = fetch_all_employees_with_this_training_status(status)
    return json.dumps(format_employees_by_status(employees)), None, None


def _handle_fetch_different_employee(arguments: Dict[str, Any], current_employee_id: Optional[str], current_employee_name: Optional[str]) -> Tuple[Any, Optional[str], Optional[str]]:
    """Handle fetch_different_employee_data tool."""
    requested_employee_id = arguments.get(KEY_EMPLOYEE_ID)
    requested_employee_name = arguments.get(KEY_EMPLOYEE_NAME)
    employee_data = fetch_employee_data(requested_employee_id, requested_employee_name)
    return format_employee_data_output(employee_data), None, None


# Tool handler registry
TOOL_HANDLERS: Dict[str, Callable[[Dict[str, Any], Optional[str], Optional[str]], Tuple[Any, Optional[str], Optional[str]]]] = {
    "check_if_employee_exists_by_id_and_first_name": _handle_check_employee_exists,
    "fetch_current_user_personal_data_and_watched_videos_data": _handle_fetch_current_user_data,
    "fetch_current_ciso_employee_data": _handle_fetch_ciso_data,
    "fetch_current_employee_training_status": _handle_fetch_training_status,
    "get_summary_and_statistics_on_all_employees_training": _handle_get_statistics,
    "get_all_employees_with_this_training_status": _handle_get_employees_by_status,
    "fetch_different_employee_data_using_id_and_first_name": _handle_fetch_different_employee,
}


def process_tool_call(
    item: Any,
    current_employee_id: Optional[str],
    current_employee_name: Optional[str]
) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
    """Process a single tool call item and return output, employee_id, and employee_name."""
    tool_name = getattr(item, "name", None)
    call_id = getattr(item, "call_id", None)
    raw_args = getattr(item, "arguments", None) or "{}"
    try:
        arguments = json.loads(raw_args)
    except Exception:
        arguments = {}
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        raise ValueError(f"Unknown tool '{tool_name}'")
    output_data, extracted_employee_id, extracted_employee_name = handler(
        arguments, current_employee_id, current_employee_name)
    function_call_output = create_function_call_output(call_id, output_data)
    return function_call_output, extracted_employee_id, extracted_employee_name


async def get_function_call_outputs(
    output: List[Any],
    current_employee_id: Optional[str] = None,
    current_employee_name: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Optional[str], Optional[str]]:
    """Process function calls from LLM output and return outputs, employee_id, and employee_name."""
    function_call_outputs: List[Dict[str, Any]] = []
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    logger.info(f"Output: {output}")
    
    for item in output or []:
        if getattr(item, KEY_TYPE, None) != FUNCTION_CALL_TYPE:
            continue

        function_call_output, extracted_employee_id, extracted_employee_name = process_tool_call(
            item, current_employee_id, current_employee_name)
        if function_call_output:
            function_call_outputs.append(function_call_output)
        # Update employee_id and employee_name if extracted (only for check_employee_exists tool)
        if extracted_employee_id is not None:
            employee_id = extracted_employee_id
        if extracted_employee_name is not None:
            employee_name = extracted_employee_name

    return function_call_outputs, employee_id, employee_name

