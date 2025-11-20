"""
Schemas for the API.
"""
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    history: list[dict]
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
