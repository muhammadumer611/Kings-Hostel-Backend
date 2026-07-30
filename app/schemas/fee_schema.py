from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

class FeeStatus(str, Enum):
    PAID = "Paid"
    PENDING = "Pending"
    OVERDUE = "Overdue"

class PaymentMethod(str, Enum):
    CASH = "Cash"
    BANK = "Bank"
    JAZZCASH = "JazzCash"
    EASYPAISA = "EasyPaisa"
    OTHER = "Other"

class FeeCreate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    student_id: str

    month: str = Field(
        ...,
        examples=["2026-08"]
    )

    due_date: str = Field(
        ...,
        examples=["2026-08-10"]
    )

    notes: Optional[str] = Field(
        default=None,
        max_length=500,
    )

class FeeUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    payment_method: Optional[PaymentMethod] = None

    transaction_id: Optional[str] = None

    payment_date: Optional[str] = None

    notes: Optional[str] = None

    status: Optional[FeeStatus] = None

class FeeResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    firebase_id: str

    fee_id: str

    student_id: str

    student_name: str

    room_number: Optional[str] = None

    block: Optional[str] = None

    month: str

    amount: float

    due_date: str

    payment_date: Optional[str] = None

    payment_method: Optional[PaymentMethod] = None

    transaction_id: Optional[str] = None

    status: FeeStatus

    notes: Optional[str] = None

    created_at: Optional[str] = None

    updated_at: Optional[str] = None

class FeeListData(BaseModel):

    total_records: int

    fees: list[FeeResponse]

class FeeListResponse(BaseModel):

    success: bool

    message: str

    data: FeeListData

    errors: Optional[list] = None

class FeeSingleResponse(BaseModel):

    success: bool

    message: str

    data: FeeResponse

    errors: Optional[list] = None

class FeeCreateResponse(BaseModel):

    success: bool

    message: str

    data: dict[str, str]

    errors: Optional[list] = None

class FeeUpdateResponse(BaseModel):

    success: bool

    message: str

    data: FeeResponse

    errors: Optional[list] = None

class FeeDeleteResponse(BaseModel):

    success: bool

    message: str

    data: Optional[dict[str, str]] = None

    errors: Optional[list] = None

class FeeDeleteResponse(BaseModel):

    success: bool

    message: str

    data: Optional[dict[str, str]] = None

    errors: Optional[list] = None

class FeeCountResponse(BaseModel):

    success: bool

    message: str

    data: dict[str, int]

    errors: Optional[list] = None

class FeeSearchResponse(BaseModel):

    success: bool

    message: str

    data: FeeListData

    errors: Optional[list] = None

