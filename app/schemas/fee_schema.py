from typing import Optional
from pydantic import BaseModel, Field


class FeeRecordCreate(BaseModel):
    student_id: str = Field(..., min_length=1)
    student_name: str = Field(..., min_length=1)
    roll_number: str = Field(..., min_length=1)
    room_number: str = Field(..., min_length=1)
    block: str = Field(..., min_length=1)
    amount: float = Field(..., ge=0)
    month: str = Field(..., min_length=1)
    due_date: str = Field(..., min_length=1)
    status: str = "Pending"
    payment_date: Optional[str] = None
    transaction_id: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class FeeRecordUpdate(BaseModel):
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    room_number: Optional[str] = None
    block: Optional[str] = None
    amount: Optional[float] = None
    month: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None
    payment_date: Optional[str] = None
    transaction_id: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None
