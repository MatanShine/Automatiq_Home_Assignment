from openai import AsyncOpenAI
from typing import Optional, List, Dict, Any, Tuple
import json
import os
import logging
from app.db.queries import employee_exists_in_database, fetch_employee_data, fetch_employee_training_status, get_statistic_summary, fetch_all_employees_with_this_training_status
from app.services.tools import (
    CHECK_IF_EMPLOYEE_EXISTS_BY_ID_AND_NAME, 
    FETCH_CURRENT_EMPLOYEE_DATA, 
    FETCH_CURRENT_EMPLOYEE_TRAINING_STATUS,
    GET_STATISTIC_SUMMARY_ON_TRAINING,
    FETCH_CURRENT_CISO_EMPLOYEE_DATA,
    GET_ALL_EMPLOYEES_WITH_THIS_TRAINING_STATUS,
    FETCH_DIFFERENT_EMPLOYEE_DATA
)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Please set it in a .env file in the project root or as an environment variable."
    )

client = AsyncOpenAI(api_key=api_key)

# Configure logger to output to stdout (appears in Docker logs)
logger = logging.getLogger("llm_client")

async def authenticate_employee(
    user_message: str,
    history: Optional[list[dict]] = None,
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Query OpenAI Responses API with optional tools.

        1. Ask model, let it emit function_call(s)
        2. Run corresponding Python functions (like employee_exists_in_database)
        3. Return message, employee_id, and employee_name (if tool was used)
     """
    messages = build_prompt(user_message, history)
    try:
        response = await client.responses.create(
            model="gpt-4o-mini",
            input=messages,
            instructions="user must give you his name and his id. if user gives you these 2, use the tool to check if the employee exists in the database. if the employee exists, ask user what can you do for him. if the employee does not exist, return an error message. tone: keep insisting",
            tools=[CHECK_IF_EMPLOYEE_EXISTS_BY_ID_AND_NAME],
            max_tool_calls=1
        )

        # Collect function calls from response.output
        function_call_outputs, extracted_employee_id, extracted_employee_name = await get_function_call_outputs(response.output)
        logger.info(f"Function call outputs: {function_call_outputs}")
        # If model didn't actually call any tools, just return its answer
        if not function_call_outputs:
            full_text = (getattr(response, "output_text", None) or "").strip()
            return {
                "message": full_text or "[Empty response from model]",
                "employee_id": None,
                "employee_name": None
            }

        return {
            "message": "Hi " + extracted_employee_name + ", how can I help you?",
            "employee_id": extracted_employee_id,
            "employee_name": extracted_employee_name
        }

    except Exception as e:
        return {
            "message": f"Error querying OpenAI API: {str(e)}",
            "employee_id": None,
            "employee_name": None
        }

async def ciso_query(user_message: str, history: Optional[list[dict]] = None, employee_id: Optional[str] = None, employee_name: Optional[str] = None) -> Tuple[str, Optional[str], Optional[str]]:
    messages = build_prompt(user_message, history)
    try:
        response = await client.responses.create(
            model="gpt-4o-mini",
            input=messages,
            instructions="you are a helpful training cybersecurity training assistant. you are given a message from the ciso and you need to answer the question. if the question is not related to the training, you need to say that you are not sure about the answer and you will ask the employee to contact the training team. tone: friendly and helpful",
            tools=[GET_STATISTIC_SUMMARY_ON_TRAINING, FETCH_CURRENT_CISO_EMPLOYEE_DATA, GET_ALL_EMPLOYEES_WITH_THIS_TRAINING_STATUS, FETCH_DIFFERENT_EMPLOYEE_DATA],
            max_tool_calls=3
        )

        # Collect function calls from response.output
        function_call_outputs, _, _ = await get_function_call_outputs(
            response.output,
            current_employee_id=employee_id,
            current_employee_name=employee_name
        )
        logger.info(f"Function call outputs: {function_call_outputs}")
        
        # If there were function calls, we need to send them back to the model for a final response
        if function_call_outputs:
            # Include the original response output (which contains function calls) and the outputs
            # The Responses API expects: messages + function calls + function call outputs
            messages_with_outputs = messages.copy()
            # Add the function calls from the original response
            for item in response.output or []:
                if getattr(item, "type", None) == "function_call":
                    messages_with_outputs.append(item)
            # Add the function call outputs
            messages_with_outputs.extend(function_call_outputs)
            logger.info(f"Messages with outputs: {function_call_outputs}")
            
            final_response = await client.responses.create(
                model="gpt-4o-mini",
                input=messages_with_outputs,
                instructions="you are a helpful training cybersecurity training assistant. you are given a message from the ciso and you need to answer the question. if the question is not related to the training, you need to say that you are not sure about the answer and you will ask the employee to contact the training team. tone: friendly and helpful",
            )
            full_text = (getattr(final_response, "output_text", None) or "").strip()
            return {
                "message": full_text or "[Empty response from model]",
                "employee_id": employee_id,
                "employee_name": employee_name
            }
        
        # If model didn't actually call any tools, just return its answer
        full_text = (getattr(response, "output_text", None) or "").strip()
        return {
            "message": full_text or "[Empty response from model]",
            "employee_id": employee_id,
            "employee_name": employee_name
        }

    except Exception as e:
        logger.error(f"Error in ciso_query: {e}")
        return {
            "message": f"Error querying OpenAI API: {str(e)}",
            "employee_id": employee_id,
            "employee_name": employee_name
        }

async def regular_employee_query(user_message: str, history: Optional[list[dict]] = None, employee_id: Optional[str] = None, employee_name: Optional[str] = None) -> Tuple[str, Optional[str], Optional[str]]:
    messages = build_prompt(user_message, history)
    try:
        response = await client.responses.create(
            model="gpt-4o-mini",
            input=messages,
            instructions="you are a helpful training cybersecurity training assistant. you are given a message from an employee and you need to answer the question. if the question is not related to the training, you need to say that you are not sure about the answer and you will ask the employee to contact the training team. tone: friendly and helpful",
            tools=[FETCH_CURRENT_EMPLOYEE_DATA, FETCH_CURRENT_EMPLOYEE_TRAINING_STATUS],
            max_tool_calls=1
        )

        # Collect function calls from response.output
        function_call_outputs, _, _ = await get_function_call_outputs(
            response.output, 
            current_employee_id=employee_id, 
            current_employee_name=employee_name
        )
        
        # If there were function calls, we need to send them back to the model for a final response
        if function_call_outputs:
            # Include the original response output (which contains function calls) and the outputs
            # The Responses API expects: messages + function calls + function call outputs
            messages_with_outputs = messages.copy()
            # Add the function calls from the original response
            for item in response.output or []:
                if getattr(item, "type", None) == "function_call":
                    messages_with_outputs.append(item)
            # Add the function call outputs
            messages_with_outputs.extend(function_call_outputs)
            logger.info(f"Messages with outputs: {function_call_outputs}")
            final_response = await client.responses.create(
                model="gpt-4o-mini",
                input=messages_with_outputs,
                instructions="you are a helpful training cybersecurity training assistant. you are given a message from an employee and you need to answer the question. if the question is not related to the training, you need to say that you are not sure about the answer and you will ask the employee to contact the training team. tone: friendly and helpful",
            )
            full_text = (getattr(final_response, "output_text", None) or "").strip()
            return {
                "message": full_text or "[Empty response from model]",
                "employee_id": employee_id,
                "employee_name": employee_name
            }
        
        # If model didn't actually call any tools, just return its answer
        full_text = (getattr(response, "output_text", None) or "").strip()
        return {
            "message": full_text or "[Empty response from model]",
            "employee_id": employee_id,
            "employee_name": employee_name
        }

    except Exception as e:
        logger.error(f"Error in regular_employee_query: {e}")
        return {
            "message": f"Error querying OpenAI API: {str(e)}",
            "employee_id": employee_id,
            "employee_name": employee_name
        }

async def get_function_call_outputs(output: List[Any], current_employee_id: Optional[str] = None, current_employee_name: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Optional[str], Optional[str]]:
    function_call_outputs: List[Dict[str, Any]] = []
    employee_id: Optional[str] = ""
    employee_name: Optional[str] = ""
    logger.info(f"Output: {output}")
    for item in output or []:
        if getattr(item, "type", None) != "function_call":
            continue

        tool_name = getattr(item, "name", None)
        call_id = getattr(item, "call_id", None)
        raw_args = getattr(item, "arguments", None) or "{}"

        try:
            arguments = json.loads(raw_args)
        except Exception:
            arguments = {}

        if tool_name == "check_if_employee_exists_by_id_and_name":
            employee_id = arguments.get("employee_id")
            employee_name = arguments.get("employee_name")

            exists = employee_exists_in_database(employee_id, employee_name)

            function_call_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps({"exists": exists}),
                }
            )
        elif tool_name == "fetch_all_current_user_data":            
            employee_data = fetch_employee_data(current_employee_id, current_employee_name)
            
            function_call_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(employee_data) if employee_data else json.dumps({"error": "Employee data not found"}),
                }
            )
        elif tool_name == "fetch_current_employee_training_status":
            training_status = fetch_employee_training_status(current_employee_id, current_employee_name)
            
            function_call_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps({"training_status": training_status}) if training_status else json.dumps({"error": "Training status not found"}),
                }
            )
        elif tool_name == "get_statistic_summary_on_training":
            statistics = get_statistic_summary()
            
            function_call_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(statistics) if statistics else json.dumps({"error": "Statistics not available"}),
                }
            )
        elif tool_name == "fetch_current_ciso_employee_data":
            employee_data = fetch_employee_data(current_employee_id, current_employee_name)
            
            function_call_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(employee_data) if employee_data else json.dumps({"error": "Employee data not found"}),
                }
            )
        elif tool_name == "get_all_employees_with_this_training_status":
            status = arguments.get("status")
            employees = fetch_all_employees_with_this_training_status(status)
            
            # Format the employee data for better readability
            if employees:
                formatted_employees = []
                for emp in employees:
                    formatted_employees.append({
                        "employee_id": emp[0],
                        "employee_name": emp[1],
                        "employee_last_name": emp[2],
                        "employee_division": emp[3] if len(emp) > 3 else None
                    })
                function_call_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": json.dumps({"employees": formatted_employees, "count": len(formatted_employees)}),
                    }
                )
            else:
                function_call_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": json.dumps({"error": "No employees found with this status", "employees": [], "count": 0}),
                    }
                )
        elif tool_name == "fetch_different_employee_data":
            requested_employee_id = arguments.get("employee_id")
            requested_employee_name = arguments.get("employee_name")
            
            employee_data = fetch_employee_data(requested_employee_id, requested_employee_name)
            
            function_call_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(employee_data) if employee_data else json.dumps({"error": "Employee data not found"}),
                }
            )
        else:
            raise ValueError(f"Unknown tool '{tool_name}'")

    return function_call_outputs, employee_id, employee_name

def build_prompt(user_message: str, history: Optional[list[dict]]) -> List[Dict[str, Any]]:
    history = history or []
    messages: List[Dict[str, Any]] = []

    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})
    return messages