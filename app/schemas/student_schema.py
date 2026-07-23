from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field


class StudentStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class HostelBlock(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class RoomType(str, Enum):
    TWO_SEATER = "2 Seater"
    THREE_SEATER = "3 Seater"
    FOUR_SEATER = "4 Seater"
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
        description="13-digit CNIC without dashes",
        examples=["3520212345671"],
    )

    phone: str = Field(
        ...,
        pattern=r"^03\d{9}$",
        description="Pakistani Mobile Number",
        examples=["03001234567"],
    )

    email: EmailStr = Field(
        ...,
        description="Student Email",
        examples=["umer@gmail.com"],
    )

    bloodGroup: Optional[str] = Field(
        default=None,
        description="Blood Group",
        examples=["O+"],
    )


class StudentGuardian(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Guardian Name",
        examples=["Muhammad Ali"],
    )

    phone: str = Field(
        ...,
        pattern=r"^03\d{9}$",
        description="Guardian Mobile Number",
        examples=["03111234567"],
    )

    cnic: str = Field(
        ...,
        pattern=r"^\d{13}$",
        description="Guardian CNIC",
        examples=["3520211111111"],
    )
class StudentAllocation(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    block: HostelBlock = Field(
        ...,
        description="Hostel Block",
        examples=["A"],
    )

    roomType: RoomType = Field(
        ...,
        description="Room Type",
        examples=["2 Seater"],
    )


class StudentCreate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    personal: StudentPersonal = Field(
        ...,
        description="Student Personal Information",
    )

    guardian: StudentGuardian = Field(
        ...,
        description="Guardian Information",
    )

    allocation: StudentAllocation = Field(
        ...,
        description="Hostel Allocation Information",
    )

    status: StudentStatus = Field(
        default=StudentStatus.ACTIVE,
        description="Student Status",
    )


class StudentUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    personal: Optional[StudentPersonal] = None

    guardian: Optional[StudentGuardian] = None

    allocation: Optional[StudentAllocation] = None

    status: Optional[StudentStatus] = None
class StudentResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    student_id: str = Field(
        ...,
        description="Generated Student ID",
    )

    firebase_id: str = Field(
        ...,
        description="Firebase Document ID",
    )

    name: str

    cnic: str

    phone: str

    email: EmailStr

    guardian_name: Optional[str] = None

    guardian_phone: Optional[str] = None

    guardian_cnic: Optional[str] = None

    block: Optional[str] = None

    room_type: Optional[str] = None

    blood_group: Optional[str] = None

    status: StudentStatus

    room_number: Optional[str] = None

    bed_number: Optional[str] = None

    monthly_fee: Optional[float] = 0

    security_deposit: Optional[float] = 0

    pending_fee: Optional[float] = 0

    fee_status: Optional[str] = None

    created_at: Optional[str] = None

    updated_at: Optional[str] = None
class StudentListData(BaseModel):

    total_students: int = Field(
        ...,
        description="Total number of students",
        examples=[25],
    )

    students: list[StudentResponse]


class StudentListResponse(BaseModel):

    success: bool

    message: str

    data: StudentListData

    errors: Optional[list] = None


class StudentSingleResponse(BaseModel):

    success: bool

    message: str

    data: StudentResponse

    errors: Optional[list] = None


class StudentCreateResponse(BaseModel):

    success: bool

    message: str

    data: dict

    errors: Optional[list] = None


class StudentDeleteResponse(BaseModel):

    success: bool

    message: str

    data: Optional[dict] = None

    errors: Optional[list] = None
class StudentSearchResponse(BaseModel):

    success: bool

    message: str

    data: StudentListData

    errors: Optional[list] = None


class StudentUpdateResponse(BaseModel):

    success: bool

    message: str

    data: StudentResponse

    errors: Optional[list] = None


class StudentCountResponse(BaseModel):

    success: bool

    message: str

    data: dict

    errors: Optional[list] = None