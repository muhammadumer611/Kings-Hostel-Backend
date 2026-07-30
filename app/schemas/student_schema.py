from enum import Enum
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
        examples=["umer@gmail.com"],
    )

    blood_group: Optional[str] = Field(
        default=None,
        max_length=5,
        description="Blood Group",
        examples=["O+"],
    )

    address: str = Field(
        ...,
        min_length=5,
        max_length=300,
        description="Student Address",
        examples=["Sargodha, Punjab"],
    )

    profile_image: Optional[str] = Field(
        default=None,
        description="Student Profile Image URL",
    )

    cnic_front_image: Optional[str] = Field(
        default=None,
        description="Student CNIC Front Image URL",
    )

    cnic_back_image: Optional[str] = Field(
        default=None,
        description="Student CNIC Back Image URL",
    )


class StudentGuardian(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    guardian_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Guardian Full Name",
        examples=["Muhammad Ali"],
    )

    guardian_phone: str = Field(
        ...,
        pattern=r"^03\d{9}$",
        description="Guardian Mobile Number",
        examples=["03111234567"],
    )

    guardian_cnic: str = Field(
        ...,
        pattern=r"^\d{13}$",
        description="13 Digit Guardian CNIC Without Dashes",
        examples=["3520211111111"],
    )

    relation: Optional[str] = Field(
        default=None,
        max_length=30,
        description="Relation with Student",
        examples=["Father"],
    )


class StudentAllocation(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    room_firebase_id: Optional[str] = Field(
        default=None,
        description="Firebase ID of Assigned Room",
        examples=["YH8Kq9M2LmNxP4RtUvW"],
    )

    bed_number: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Allocated Bed Number",
        examples=["Bed-01"],
    )

    joining_date: Optional[str] = Field(
        default=None,
        description="Hostel Joining Date (ISO Format)",
        examples=["2026-07-29"],
    )

    remarks: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Allocation Remarks",
        examples=["Shifted from Room 101"],
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
        description="Room Allocation Information",
    )

    status: StudentStatus = Field(
        default=StudentStatus.ACTIVE,
        description="Student Status",
    )


class StudentUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    personal: Optional[StudentPersonalUpdate]

    guardian: Optional[StudentGuardianUpdate]
    
    allocation: Optional[StudentAllocationUpdate]

    guardian: Optional[StudentGuardian] = None

    allocation: Optional[StudentAllocation] = None

    status: Optional[StudentStatus] = None


class StudentResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    # Student IDs
    student_id: str
    firebase_id: str

    # Personal Information
    name: str
    cnic: str
    phone: str
    email: Optional[EmailStr] = None

    blood_group: Optional[str] = None
    address: Optional[str] = None

    profile_image: Optional[str] = None
    cnic_front_image: Optional[str] = None
    cnic_back_image: Optional[str] = None

    # Guardian Information
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_cnic: Optional[str] = None
    relation: Optional[str] = None

    # Room Information
    room_firebase_id: Optional[str] = None
    room_number: Optional[str] = None
    floor: Optional[int] = None
    bed_number: Optional[str] = None

    # Fee Information
    monthly_fee: float = 0.0
    security_deposit: float = 0.0
    pending_fee: float = 0.0
    fee_status: Optional[FeeStatus] = None

    # Student Status
    status: StudentStatus

    # Dates
    joining_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class StudentListData(BaseModel):

    total_students: int = Field(
        ...,
        description="Total Students",
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

    data: dict[str, str]

    errors: Optional[list] = None


class StudentUpdateResponse(BaseModel):

    success: bool

    message: str

    data: StudentResponse

    errors: Optional[list] = None


class StudentDeleteResponse(BaseModel):

    success: bool

    message: str

    data: Optional[dict[str, str]] = None

    errors: Optional[list] = None


class StudentSearchResponse(BaseModel):

    success: bool

    message: str

    data: StudentListData

    errors: Optional[list] = None


class StudentCountResponse(BaseModel):

    success: bool

    message: str

    data: dict[str, int]

    errors: Optional[list] = None