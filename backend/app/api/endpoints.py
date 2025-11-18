from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse
from app.services.llm_client import query_llm
from app.services.tools import CHECK_IF_EMPLOYEE_EXISTS_BY_ID_AND_NAME
from app.db.queries import employee_exists_in_database

api_router = APIRouter()

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for direct LLM interaction.
    No authentication required.
    """
    # Query LLM directly (uses default system prompt)
    if request.employee_id and request.employee_name and employee_exists_in_database(request.employee_id, request.employee_name):
            # response = await query_llm(request.message, history=request.history)
            return ChatResponse(
                message="logged in",
                employee_id=request.employee_id,
                employee_name=request.employee_name
            )
    else:
        response = await query_llm(request.message, instructions="user must give you his name and his id. if user gives you these 2, use the tool to check if the employee exists in the database. if the employee exists, ask user what can you do for him. if the employee does not exist, return an error message. tone: keep insisting", history=request.history, tools=[CHECK_IF_EMPLOYEE_EXISTS_BY_ID_AND_NAME])
        return ChatResponse(
            message=response["message"],
            employee_id=response["employee_id"],
            employee_name=response["employee_name"]
        )

