from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator


# ============================================================
# ENUMS
# ============================================================


class StudentStatus(str, Enum):
    ACTIVE = "Active"
    ALUMNI = "Alumni"


class FeeStatus(str, Enum):
    PAID = "Paid"
    PENDING = "Pending"


class AllocationStatus(str, Enum):
    CURRENT = "Current"
    TRANSFERRED = "Transferred"
    COMPLETED = "Completed"


# ============================================================
# PERSONAL INFORMATION
# ============================================================


class StudentPersonal(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Student full name",
        examples=["Muhammad Umer"],
    )

    cnic: str = Field(
        ...,
        pattern=r"^\d{13}$",
        description="13 digit CNIC without dashes",
        examples=["3520212345671"],
    )

    phone: str = Field(
        ...,
        pattern=r"^03\d{9}$",
        description="Pakistani mobile number",
        examples=["03001234567"],
    )

    email: Optional[EmailStr] = Field(
        default=None,
        description="Student email address",
    )

    blood_group: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=5,
        description="Student blood group",
        examples=["O+"],
    )

    address: str = Field(
        ...,
        min_length=5,
        max_length=300,
        description="Permanent/current address",
    )

    profile_image: Optional[str] = Field(
        default=None,
        description="Student profile image URL",
    )

    cnic_front_image: Optional[str] = Field(
        default=None,
        description="CNIC front image URL",
    )

    cnic_back_image: Optional[str] = Field(
        default=None,
        description="CNIC back image URL",
    )


class StudentPersonalUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    cnic: Optional[str] = Field(
        default=None,
        pattern=r"^\d{13}$",
    )

    phone: Optional[str] = Field(
        default=None,
        pattern=r"^03\d{9}$",
    )

    email: Optional[EmailStr] = None

    blood_group: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=5,
    )

    address: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=300,
    )

    profile_image: Optional[str] = None

    cnic_front_image: Optional[str] = None

    cnic_back_image: Optional[str] = None


# ============================================================
# GUARDIAN INFORMATION
# ============================================================


class StudentGuardian(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    guardian_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Guardian full name",
    )

    guardian_phone: str = Field(
        ...,
        pattern=r"^03\d{9}$",
        description="Guardian mobile number",
    )

    guardian_cnic: str = Field(
        ...,
        pattern=r"^\d{13}$",
        description="Guardian CNIC",
    )

    relation: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=30,
        description="Relationship with student",
        examples=["Father"],
    )


class StudentGuardianUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    guardian_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    guardian_phone: Optional[str] = Field(
        default=None,
        pattern=r"^03\d{9}$",
    )

    guardian_cnic: Optional[str] = Field(
        default=None,
        pattern=r"^\d{13}$",
    )

    relation: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=30,
    )


# ============================================================
# CURRENT ROOM ALLOCATION
# ============================================================


class StudentAllocation(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    block: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    room_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    room_firebase_id: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    room_number: Optional[str] = Field(
        default=None,
        max_length=20,
    )

    floor: Optional[int] = Field(
        default=None,
        ge=0,
    )

    bed_number: Optional[str] = Field(
        default=None,
        max_length=20,
    )

    joining_date: Optional[datetime] = None

    remarks: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    monthly_fee: Optional[float] = Field(
        default=None,
        ge=0,
    )

    security_deposit: Optional[float] = Field(
        default=None,
        ge=0,
    )

    @field_validator("room_number")
    @classmethod
    def normalize_room_number(
        cls,
        value: Optional[str],
    ) -> Optional[str]:

        if value is None:
            return None

        value = str(value).strip().upper()

        if not value:
            raise ValueError("Room number cannot be empty.")

        return value


class StudentAllocationUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    block: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    room_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    room_firebase_id: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    room_number: Optional[str] = Field(
        default=None,
        max_length=20,
    )

    floor: Optional[int] = Field(
        default=None,
        ge=0,
    )

    bed_number: Optional[str] = Field(
        default=None,
        max_length=20,
    )

    joining_date: Optional[datetime] = None

    remarks: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    monthly_fee: Optional[float] = Field(
        default=None,
        ge=0,
    )

    security_deposit: Optional[float] = Field(
        default=None,
        ge=0,
    )

    @field_validator("room_number")
    @classmethod
    def normalize_room_number(
        cls,
        value: Optional[str],
    ) -> Optional[str]:

        if value is None:
            return None

        value = str(value).strip().upper()

        if not value:
            raise ValueError("Room number cannot be empty.")

        return value


# ============================================================
# ROOM ALLOCATION HISTORY
# ============================================================


class StudentRoomHistory(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    room_firebase_id: str

    room_number: str

    floor: Optional[int] = None

    bed_number: Optional[str] = None

    monthly_fee: float = Field(
        default=0,
        ge=0,
    )

    security_deposit: float = Field(
        default=0,
        ge=0,
    )

    joined_at: datetime

    left_at: Optional[datetime] = None

    status: AllocationStatus = AllocationStatus.CURRENT

    remarks: Optional[str] = Field(
        default=None,
        max_length=500,
    )


# ============================================================
# FEE INFORMATION
# ============================================================


class StudentFeeSummary(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    monthly_fee: float = Field(
        default=0,
        ge=0,
    )

    security_deposit: float = Field(
        default=0,
        ge=0,
    )

    pending_fee: float = Field(
        default=0,
        ge=0,
    )

    fee_status: FeeStatus = FeeStatus.PENDING

    last_fee_payment_date: Optional[datetime] = None


class StudentFeeHistory(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    amount: float = Field(
        ...,
        gt=0,
    )

    month: str = Field(
        ...,
        min_length=7,
        max_length=7,
        description="Fee month in YYYY-MM format",
        examples=["2026-08"],
    )

    paid_at: Optional[datetime] = None

    status: FeeStatus = FeeStatus.PENDING

    remarks: Optional[str] = Field(
        default=None,
        max_length=500,
    )


# ============================================================
# STUDENT CREATE
# ============================================================


class StudentCreate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    personal: StudentPersonal

    guardian: StudentGuardian

    allocation: Optional[StudentAllocation] = None

    status: StudentStatus = StudentStatus.ACTIVE


# ============================================================
# STUDENT UPDATE
# ============================================================


class StudentUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    personal: Optional[StudentPersonalUpdate] = None

    guardian: Optional[StudentGuardianUpdate] = None

    allocation: Optional[StudentAllocationUpdate] = None

    status: Optional[StudentStatus] = None


# ============================================================
# STUDENT RESPONSE
# ============================================================


class StudentResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    # --------------------------------------------------------
    # IDs
    # --------------------------------------------------------

    student_id: Optional[str] = None

    firebase_id: Optional[str] = None

    # --------------------------------------------------------
    # Personal Information
    # --------------------------------------------------------

    name: str

    cnic: str

    phone: str

    email: Optional[EmailStr] = None

    blood_group: Optional[str] = None

    address: Optional[str] = None

    profile_image: Optional[str] = None

    cnic_front_image: Optional[str] = None

    cnic_back_image: Optional[str] = None

    # --------------------------------------------------------
    # Guardian
    # --------------------------------------------------------

    guardian_name: Optional[str] = None

    guardian_phone: Optional[str] = None

    guardian_cnic: Optional[str] = None

    relation: Optional[str] = None

    # --------------------------------------------------------
    # Current Allocation
    # --------------------------------------------------------

    block: Optional[str] = None

    room_type: Optional[str] = None

    room_firebase_id: Optional[str] = None

    room_number: Optional[str] = None

    floor: Optional[int] = None

    bed_number: Optional[str] = None

    joining_date: Optional[datetime] = None

    # --------------------------------------------------------
    # Fees
    # --------------------------------------------------------

    monthly_fee: float = 0.0

    security_deposit: float = 0.0

    pending_fee: float = 0.0

    fee_status: FeeStatus = FeeStatus.PENDING

    last_fee_payment_date: Optional[datetime] = None

    # --------------------------------------------------------
    # Student Status
    # --------------------------------------------------------

    status: StudentStatus = StudentStatus.ACTIVE

    # --------------------------------------------------------
    # Leaving / Alumni
    # --------------------------------------------------------

    leaving_date: Optional[datetime] = None

    leaving_reason: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    # --------------------------------------------------------
    # Remarks
    # --------------------------------------------------------

    remarks: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    # --------------------------------------------------------
    # Audit
    # --------------------------------------------------------

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


# ============================================================
# STUDENT DETAIL / HISTORY RESPONSE
# ============================================================


class StudentDetailResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    student: StudentResponse

    room_history: list[StudentRoomHistory] = Field(
        default_factory=list
    )

    fee_history: list[StudentFeeHistory] = Field(
        default_factory=list
    )


class StudentDetailSingleResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentDetailResponse] = None

    errors: Any = None


# ============================================================
# STUDENT LIST
# ============================================================


class StudentListData(BaseModel):

    total_students: int

    students: list[StudentResponse]


class StudentListResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentListData] = None

    errors: Any = None


# ============================================================
# SINGLE STUDENT
# ============================================================


class StudentSingleResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentResponse] = None

    errors: Any = None


# ============================================================
# CREATE RESPONSE
# ============================================================


class StudentCreateData(BaseModel):

    student_id: str

    firebase_id: str


class StudentCreateResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentCreateData] = None

    errors: Any = None


# ============================================================
# UPDATE RESPONSE
# ============================================================


class StudentUpdateResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentResponse] = None

    errors: Any = None


# ============================================================
# DELETE / ALUMNI RESPONSE
# ============================================================


class StudentDeleteData(BaseModel):

    student_id: Optional[str] = None


class StudentDeleteResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentDeleteData] = None

    errors: Any = None


# ============================================================
# SEARCH RESPONSE
# ============================================================


class StudentSearchResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentListData] = None

    errors: Any = None


# ============================================================
# COUNT RESPONSE
# ============================================================


class StudentCountData(BaseModel):

    total_students: int


class StudentCountResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentCountData] = None

    errors: Any = None