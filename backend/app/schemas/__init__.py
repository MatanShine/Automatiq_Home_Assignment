from pydantic import BaseModel
from typing import Optional


class EmployeeBase(BaseModel):
    EMPLOYEE_ID: str
    EMPLOYEE_NAME: str
    EMPLOYEE_LAST_NAME: str
    EMPLOYEE_DIVISION: str
    FINISHED_FIRST_VIDEO: int
    FINISHED_FIRST_VIDEO_DATE: Optional[str] = None
    FINISHED_SECOND_VIDEO: int
    FINISHED_SECOND_VIDEO_DATE: Optional[str] = None
    FINISHED_THIRD_VIDEO: int
    FINISHED_THIRD_VIDEO_DATE: Optional[str] = None
    FINISHED_FOURTH_VIDEO: int
    FINISHED_FOURTH_VIDEO_DATE: Optional[str] = None

    class Config:
        from_attributes = True



class ChatRequest(BaseModel):
    message: str
    history: list[dict]
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None

