from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class RoomStatus(str, Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    MAINTENANCE = "Maintenance"


class HostelBlock(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class RoomType(str, Enum):
    TWO_SEATER = "2 Seater"
    THREE_SEATER = "3 Seater"
    FOUR_SEATER = "4 Seater"
class RoomCreate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    room_number: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Unique Room Number",
        examples=["A-101"],
    )

    block: HostelBlock = Field(
        ...,
        description="Hostel Block",
        examples=["A"],
    )

    floor: int = Field(
        ...,
        ge=0,
        description="Floor Number",
        examples=[1],
    )

    room_type: RoomType = Field(
        ...,
        description="Room Type",
        examples=["2 Seater"],
    )

    total_beds: int = Field(
        ...,
        ge=1,
        le=10,
        description="Total Beds",
        examples=[2],
    )

    occupied_beds: int = Field(
        default=0,
        ge=0,
        description="Occupied Beds",
        examples=[0],
    )

    status: RoomStatus = Field(
        default=RoomStatus.AVAILABLE,
        description="Room Status",
    )

    price_per_month: float = Field(
        default=0,
        ge=0,
        description="Monthly Room Fee",
        examples=[12000],
    )

    security_deposit: float = Field(
        default=0,
        ge=0,
        description="Security Deposit",
        examples=[5000],
    )

    amenities: Optional[List[str]] = Field(
        default=[],
        description="Room Amenities",
        examples=[["WiFi", "AC", "Attached Washroom"]],
    )


class RoomUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    room_number: Optional[str] = None

    block: Optional[HostelBlock] = None

    floor: Optional[int] = Field(
        default=None,
        ge=0,
    )

    room_type: Optional[RoomType] = None

    total_beds: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
    )

    occupied_beds: Optional[int] = Field(
        default=None,
        ge=0,
    )

    status: Optional[RoomStatus] = None

    price_per_month: Optional[float] = Field(
        default=None,
        ge=0,
    )

    security_deposit: Optional[float] = Field(
        default=None,
        ge=0,
    )

    amenities: Optional[List[str]] = None
class RoomResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    firebase_id: str = Field(
        ...,
        description="Firebase Document ID",
    )

    room_number: str

    block: HostelBlock

    floor: int

    room_type: RoomType

    total_beds: int

    occupied_beds: int

    available_beds: int

    status: RoomStatus

    price_per_month: float

    security_deposit: float

    amenities: List[str] = []

    created_at: Optional[str] = None

    updated_at: Optional[str] = None


class RoomListData(BaseModel):

    total_rooms: int = Field(
        ...,
        description="Total number of rooms",
        examples=[120],
    )

    rooms: list[RoomResponse]
class RoomCreateResponse(BaseModel):

    success: bool

    message: str

    data: dict

    errors: Optional[list] = None


class RoomSingleResponse(BaseModel):

    success: bool

    message: str

    data: RoomResponse

    errors: Optional[list] = None


class RoomListResponse(BaseModel):

    success: bool

    message: str

    data: RoomListData

    errors: Optional[list] = None


class RoomUpdateResponse(BaseModel):

    success: bool

    message: str

    data: RoomResponse

    errors: Optional[list] = None


class RoomDeleteResponse(BaseModel):

    success: bool

    message: str

    data: Optional[dict] = None

    errors: Optional[list] = None
class RoomSearchResponse(BaseModel):

    success: bool

    message: str

    data: RoomListData

    errors: Optional[list] = None


class RoomCountResponse(BaseModel):

    success: bool

    message: str

    data: dict

    errors: Optional[list] = None


class AvailableRoomResponse(BaseModel):

    success: bool

    message: str

    data: RoomListData

    errors: Optional[list] = None


class OccupiedRoomResponse(BaseModel):

    success: bool

    message: str

    data: RoomListData

    errors: Optional[list] = None