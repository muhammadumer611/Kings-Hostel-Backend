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
    year: int = Field(
        ...,
        examples=[2026]
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


    student_id: str

    student_name: str

    room_number: Optional[str] = None

    block: Optional[str] = None

    month: str

    amount: float = 0.0

    due_date: str

    payment_date: Optional[str] = None

    payment_method: Optional[PaymentMethod] = None

    transaction_id: Optional[str] = None

    status: FeeStatus

    notes: Optional[str] = None

    created_at: Optional[str] = None

    updated_at: Optional[str] = None

    discount: float = 0.0

    late_fee: float =0.0

    remaining_amount: float =0.0

    receipt_no: Optional[str] = None

    student_firebase_id: Optional[str] = None

    approved_by: Optional[str] = None

    approved_at: Optional[str] = None

    is_late: bool = False


class FeeListData(BaseModel):

    total_records: int

    fee_records: list[FeeResponse]


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


class ReceiptSearchRequest(BaseModel):

    receipt_no: str


class StudentFeeRequest(BaseModel):

    student_id: str


class StudentMonthFeeRequest(BaseModel):

    student_id: str

    month: str

    year: int


class FeeStatisticsData(BaseModel):

    total_fees: int

    pending_count: int

    paid_count: int

    collected_amount: float

    pending_amount: float

    total_late_fee: float


class FeeDashboardResponse(BaseModel):

    success: bool

    message: str

    data: FeeStatisticsData

    errors: Optional[list] = None


class FeeStatisticsResponse(BaseModel):

    success: bool

    message: str

    data: FeeStatisticsData

    errors: Optional[list] = None


class FeeApproveRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    payment_date: str

    payment_method: PaymentMethod

    approved_by: str

    transaction_id: Optional[str] = None


class FeeDeleteResponse(BaseModel):

    success: bool

    message: str

    data: Optional[dict[str, str]] = None

    errors: Optional[list] = None


class FeeEnableResponse(BaseModel):

    success: bool

    message: str

    data: Optional[dict[str, str]] = None

    errors: Optional[list] = None


class FeeDisableResponse(BaseModel):

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