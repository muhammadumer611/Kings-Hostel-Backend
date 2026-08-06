from enum import Enum
from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field

class StudentStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class FeeStatus(str, Enum):
    PAID = "Paid"
    PENDING = "Pending"

class StudentPersonal(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Student Full Name",
        examples=["Muhammad Umer"],
    )

    cnic: str = Field(
        ...,
        pattern=r"^\d{13}$",
        description="13 Digit CNIC Without Dashes",
        examples=["3520212345671"],
    )

    phone: str = Field(
        ...,
        pattern=r"^03\d{9}$",
        description="Pakistani Mobile Number",
        examples=["03001234567"],
    )

    email: Optional[EmailStr] = Field(
        default=None,
        description="Student Email",
    )

    blood_group: Optional[str] = Field(
        default=None,
        max_length=5,
        examples=["O+"],
    )

    address: str = Field(
        ...,
        min_length=5,
        max_length=300,
    )

    profile_image: Optional[str] = None

    cnic_front_image: Optional[str] = None

    cnic_back_image: Optional[str] = None

class StudentPersonalUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    name: Optional[str] = Field(default=None, min_length=2, max_length=100)

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

class StudentGuardian(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    guardian_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    guardian_phone: str = Field(
        ...,
        pattern=r"^03\d{9}$",
    )

    guardian_cnic: str = Field(
        ...,
        pattern=r"^\d{13}$",
    )

    relation: Optional[str] = Field(
        default=None,
        max_length=30,
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
        max_length=30,
    )

class StudentAllocation(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    block: Optional[str] = None

    room_type: Optional[str] = None

    room_firebase_id: Optional[str] = None

    room_number: Optional[str] = None

    floor: Optional[int] = None

    bed_number: Optional[str] = None

    joining_date: Optional[str] = None

    remarks: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    monthly_fee: Optional[float] = None

    security_deposit: Optional[float] = None

class StudentAllocationUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    block: Optional[str] = None

    room_type: Optional[str] = None

    room_firebase_id: Optional[str] = None

    room_number: Optional[str] = None

    floor: Optional[int] = None

    bed_number: Optional[str] = None

    joining_date: Optional[str] = None

    remarks: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    monthly_fee: Optional[float] = None

    security_deposit: Optional[float] = None

class StudentCreate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    personal: StudentPersonal

    guardian: StudentGuardian

    allocation: Optional[StudentAllocation] = None

    status: StudentStatus = StudentStatus.ACTIVE

class StudentUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    personal: Optional[StudentPersonalUpdate] = None

    guardian: Optional[StudentGuardianUpdate] = None

    allocation: Optional[StudentAllocationUpdate] = None

    status: Optional[StudentStatus] = None

class StudentResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    # IDs
    student_id: Optional[str] = None
    firebase_id: Optional[str] = None

    # Personal
    name: str
    cnic: str
    phone: str
    email: Optional[EmailStr] = None

    blood_group: Optional[str] = None
    address: Optional[str] = None

    profile_image: Optional[str] = None
    cnic_front_image: Optional[str] = None
    cnic_back_image: Optional[str] = None

    # Guardian
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_cnic: Optional[str] = None
    relation: Optional[str] = None

    # Allocation
    block: Optional[str] = None
    room_type: Optional[str] = None
    room_firebase_id: Optional[str] = None
    room_number: Optional[str] = None
    floor: Optional[int] = None
    bed_number: Optional[str] = None

    # Fee
    monthly_fee: float = 0.0
    security_deposit: float = 0.0
    pending_fee: float = 0.0
    fee_status: FeeStatus = FeeStatus.PENDING

    # Status
    status: StudentStatus = StudentStatus.ACTIVE

    # Other
    joining_date: Optional[str] = None
    remarks: Optional[str] = None

    # Audit
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class StudentListData(BaseModel):

    total_students: int

    students: list[StudentResponse]

class StudentListResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentListData] = None

    errors: Any = None

class StudentSingleResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentResponse] = None

    errors: Any = None

class StudentCreateData(BaseModel):

    student_id: str

    firebase_id: str


class StudentCreateResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentCreateData] = None

    errors: Any = None

class StudentUpdateResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentResponse] = None

    errors: Any = None

class StudentDeleteData(BaseModel):

    student_id: Optional[str] = None


class StudentDeleteResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentDeleteData] = None

    errors: Any = None

class StudentSearchResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentListData] = None

    errors: Any = None

class StudentCountData(BaseModel):

    total_students: int

class StudentCountResponse(BaseModel):

    success: bool

    message: str

    data: Optional[StudentCountData] = None

    errors: Any = None