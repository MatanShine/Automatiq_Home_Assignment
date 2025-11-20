"""
API endpoints for the application.
"""
from fastapi import APIRouter
from app.schemas.api_schemas import ChatRequest, ChatResponse
from app.services.llm.llm_client import authenticate_employee, regular_employee_query, ciso_query
from app.db.verifiers import employee_exists_in_database, is_ciso

api_router = APIRouter()

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for direct LLM interaction.
    No authentication required.
    """
    # Query LLM directly (uses default system prompt)
    if request.employee_id and request.employee_name and employee_exists_in_database(request.employee_id, request.employee_name):
        if is_ciso(request.employee_id, request.employee_name):
            response = await ciso_query(request.message, history=request.history, employee_id=request.employee_id, employee_name=request.employee_name)
        else:
            response = await regular_employee_query(request.message, history=request.history, employee_id=request.employee_id, employee_name=request.employee_name)
        return ChatResponse(
            message=response["message"],
            employee_id=request.employee_id,
            employee_name=request.employee_name
        )
    else:
        response = await authenticate_employee(request.message, history=request.history)
        return ChatResponse(
            message=response["message"],
            employee_id=response["employee_id"],
            employee_name=response["employee_first_name"]
        )

