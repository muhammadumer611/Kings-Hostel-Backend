from typing import Optional
from pydantic import BaseModel, Field


class ComplaintCreate(BaseModel):
    student_id: str = Field(..., min_length=1)
    student_name: str = Field(..., min_length=1)
    room_number: str = Field(..., min_length=1)
    block: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    priority: str = Field(..., min_length=1)
    status: str = "Pending"
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None


class ComplaintUpdate(BaseModel):
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    room_number: Optional[str] = None
    block: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
