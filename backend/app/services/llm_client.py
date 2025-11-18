from openai import AsyncOpenAI
from typing import Optional, List, Dict, Any, Tuple
import json
import os
import logging
import sys
from app.db.queries import employee_exists_in_database

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Please set it in a .env file in the project root or as an environment variable."
    )

client = AsyncOpenAI(api_key=api_key)

# Configure logger to output to stdout (appears in Docker logs)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

async def query_llm(
    user_message: str,
    instructions: str,
    history: Optional[list[dict]] = None,
    tools: Optional[list[dict]] = None,
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Query OpenAI Responses API with optional tools.

    - If `tools` is provided: performs a tool-calling round trip:
        1. Ask model, let it emit function_call(s)
        2. Run corresponding Python functions (like employee_exists_in_database)
        3. Call model again with function_call_output items
        4. Return message, employee_id, and employee_name (if tool was used)
     """

    # Build conversation as messages (history + current user message)
    messages = build_prompt(user_message, history)


    try:
        response = await client.responses.create(
            model="gpt-4o-mini",
            input=messages,
            instructions=instructions,
            tools=tools,
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
        # --- Second call: send function_call_output items back to the model ---
        second_response = await client.responses.create(
            model="gpt-4o-mini",
            previous_response_id=response.id,
            input=function_call_outputs,
        )
        logger.info(f"Second response: {second_response.output_text}")
        full_text = (getattr(second_response, "output_text", None) or "").strip()
        return {
            "message": full_text or "[Empty response from model]",
            "employee_id": extracted_employee_id,
            "employee_name": extracted_employee_name
        }

    except Exception as e:
        return {
            "message": f"Error querying OpenAI API: {str(e)}",
            "employee_id": None,
            "employee_name": None
        }

async def get_function_call_outputs(output: List[Any]) -> Tuple[List[Dict[str, Any]], Optional[str], Optional[str]]:
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

            exists = employee_exists_in_database(employee_id.lower(), employee_name.lower())

            function_call_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps({"exists": exists}),
                }
            )
        else:
            function_call_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(
                        {"error": f"Unknown tool '{tool_name}'"}
                    ),
                }
            )
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