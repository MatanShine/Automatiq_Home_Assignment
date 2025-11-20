"""
Configuration constants for LLM client.
"""

# Model configuration
MODEL_NAME = "gpt-4o-mini"
FUNCTION_CALL_TYPE = "function_call"
FUNCTION_CALL_OUTPUT_TYPE = "function_call_output"
EMPTY_RESPONSE_MESSAGE = "[Empty response from model]"
ERROR_MESSAGE_PREFIX = "Error querying OpenAI API:"

# Tool name constants
TOOL_CHECK_EMPLOYEE_EXISTS = "check_if_employee_exists_by_id_and_first_name"
TOOL_FETCH_CURRENT_USER_DATA = "fetch_current_user_personal_data_and_watched_videos_data"
TOOL_FETCH_TRAINING_STATUS = "fetch_current_employee_training_status"
TOOL_GET_STATISTICS = "get_summary_and_statistics_on_all_employees_training"
TOOL_FETCH_CISO_DATA = "fetch_current_ciso_employee_data"
TOOL_GET_EMPLOYEES_BY_STATUS = "get_all_employees_with_this_training_status"
TOOL_FETCH_DIFFERENT_EMPLOYEE = "fetch_different_employee_data_using_id_and_first_name"

# Response keys
KEY_MESSAGE = "message"
KEY_EMPLOYEE_ID = "employee_id"
KEY_EMPLOYEE_NAME = "employee_first_name"
KEY_OUTPUT = "output"
KEY_EXISTS = "exists"
KEY_CALL_ID = "call_id"
KEY_TYPE = "type"

# Instructions
INSTRUCTION_AUTHENTICATE = (
    "user must give you his name and his id. if user gives you these 2, use the tool to check if the employee exists in the database. "
    "if the employee exists, ask user what can you do for him. if the employee does not exist, return an error message. tone: keep insisting"
)
INSTRUCTION_TRAINING_ASSISTANT = (
    "you are a helpful training cybersecurity training assistant. you are given a message from {user_type} and you need to answer the question. "
    "if the question is not related to the training, you need to say that you are not sure about the answer and you will ask the employee to contact the training team. "
    "tone: friendly and helpful"
)

