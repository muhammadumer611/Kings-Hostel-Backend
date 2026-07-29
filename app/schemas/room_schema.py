from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator


class RoomCreate(BaseModel):

    model_config = ConfigDict(extra="forbid")

    room_number: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Unique Room Number",
        examples=["101"],
    )

    floor: int = Field(
        ...,
        ge=0,
        description="Floor Number",
        examples=[1],
    )

    total_beds: int = Field(
        ...,
        ge=1,
        le=20,
        description="Total Beds",
        examples=[4],
    )

    monthly_fee: float = Field(
        ...,
        gt=0,
        description="Monthly Fee",
        examples=[12000],
    )

    security_deposit: float = Field(
        default=0,
        ge=0,
        description="Security Deposit",
        examples=[5000],
    )

    

    @field_validator("room_number")
    @classmethod
    def validate_room_number(cls, value: str) -> str:
        trimmed_value = str(value or "").strip().upper()
        if not trimmed_value:
            raise ValueError("Room number cannot be empty.")
        return trimmed_value

class RoomUpdate(BaseModel):

    model_config = ConfigDict(extra="forbid")

    room_number: Optional[str] = None

    floor: Optional[int] = Field(default=None, ge=0)

    total_beds: Optional[int] = Field(default=None, ge=1, le=20)

    monthly_fee: Optional[float] = Field(default=None, gt=0)

    security_deposit: Optional[float] = Field(default=None, ge=0)

    is_active: Optional[bool] = None

    @field_validator("room_number")
    @classmethod
    def validate_room_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        trimmed_value = str(value).strip().upper()

        if not trimmed_value:
            raise ValueError("Room number cannot be empty.")

        return trimmed_value

        
class RoomResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    firebase_id: str = Field(..., description="Firebase Document ID")

    room_number: str

    floor: int

    total_beds: int

    occupied_beds: int

    available_beds: int

    status: str

    monthly_fee: float

    security_deposit: float

    is_active: bool

    current_students: list[str] = Field(default_factory=list)

    

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



class RoomListData(BaseModel):

    total_rooms: int = Field(..., description="Total Rooms", examples=[50])

    rooms: list[RoomResponse]


class RoomCreateData(BaseModel):

    firebase_id: str = Field(
        ...,
        description="Firebase Room Document ID",
    )


class RoomCreateResponse(BaseModel):

    success: bool

    message: str

    data: RoomCreateData

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