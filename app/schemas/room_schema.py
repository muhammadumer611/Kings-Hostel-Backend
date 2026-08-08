from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================
# ROOM STATUS
# ============================================================

class RoomStatus:
    AVAILABLE = "Available"
    PARTIALLY_OCCUPIED = "Partially Occupied"
    FULL = "Full"
    INACTIVE = "Inactive"


# ============================================================
# ROOM CREATE
# ============================================================

class RoomCreate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    room_number: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Unique room number.",
        examples=["101"],
    )

    floor: int = Field(
        ...,
        ge=0,
        description="Floor number. Ground floor = 0.",
        examples=[1],
    )

    total_beds: int = Field(
        ...,
        ge=1,
        le=20,
        description="Total number of beds in the room.",
        examples=[4],
    )

    monthly_fee: float = Field(
        ...,
        gt=0,
        description="Monthly fee for the room/student.",
        examples=[12000],
    )

    security_deposit: float = Field(
        default=0,
        ge=0,
        description="Security deposit.",
        examples=[5000],
    )

    @field_validator("room_number")
    @classmethod
    def validate_room_number(cls, value: str) -> str:

        value = str(value).strip().upper()

        if not value:
            raise ValueError(
                "Room number cannot be empty."
            )

        return value


# ============================================================
# ROOM UPDATE
# ============================================================

class RoomUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    room_number: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    floor: Optional[int] = Field(
        default=None,
        ge=0,
    )

    total_beds: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
    )

    monthly_fee: Optional[float] = Field(
        default=None,
        gt=0,
    )

    security_deposit: Optional[float] = Field(
        default=None,
        ge=0,
    )

    is_active: Optional[bool] = None

    @field_validator("room_number")
    @classmethod
    def validate_room_number(
        cls,
        value: Optional[str],
    ) -> Optional[str]:

        if value is None:
            return None

        value = str(value).strip().upper()

        if not value:
            raise ValueError(
                "Room number cannot be empty."
            )

        return value


# ============================================================
# ROOM RESPONSE
# ============================================================

class RoomResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    firebase_id: str = Field(
        ...,
        description="Firebase document ID.",
    )

    room_number: str = Field(
        ...,
        description="Unique room number.",
    )

    floor: int = Field(
        ...,
        ge=0,
    )

    total_beds: int = Field(
        ...,
        ge=1,
    )

    occupied_beds: int = Field(
        ...,
        ge=0,
    )

    available_beds: int = Field(
        ...,
        ge=0,
    )

    status: str = Field(
        ...,
        description=(
            "Room status: Available, Partially Occupied, "
            "Full, or Inactive."
        ),
    )

    monthly_fee: float = Field(
        ...,
        ge=0,
    )

    security_deposit: float = Field(
        ...,
        ge=0,
    )

    is_active: bool

    current_students: list[str] = Field(
        default_factory=list,
        description=(
            "Student IDs currently allocated to this room."
        ),
    )

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


# ============================================================
# ROOM LIST DATA
# ============================================================

class RoomListData(BaseModel):

    total_rooms: int = Field(
        ...,
        ge=0,
    )

    rooms: list[RoomResponse] = Field(
        default_factory=list,
    )


# ============================================================
# ROOM CREATE DATA
# ============================================================

class RoomCreateData(BaseModel):

    firebase_id: str = Field(
        ...,
        description="Firebase room document ID.",
    )


# ============================================================
# ROOM CREATE RESPONSE
# ============================================================

class RoomCreateResponse(BaseModel):

    success: bool

    message: str

    data: RoomCreateData

    errors: Optional[list] = None


# ============================================================
# ROOM SINGLE RESPONSE
# ============================================================

class RoomSingleResponse(BaseModel):

    success: bool

    message: str

    data: RoomResponse

    errors: Optional[list] = None


# ============================================================
# ROOM LIST RESPONSE
# ============================================================

class RoomListResponse(BaseModel):

    success: bool

    message: str

    data: RoomListData

    errors: Optional[list] = None


# ============================================================
# ROOM UPDATE RESPONSE
# ============================================================

class RoomUpdateResponse(BaseModel):

    success: bool

    message: str

    data: RoomResponse

    errors: Optional[list] = None


# ============================================================
# ROOM DELETE / DISABLE DATA
# ============================================================

class RoomDeleteData(BaseModel):

    firebase_id: str

    room_number: str

    disabled: bool = True


# ============================================================
# ROOM DELETE / DISABLE RESPONSE
# ============================================================

class RoomDeleteResponse(BaseModel):

    success: bool

    message: str

    data: Optional[RoomDeleteData] = None

    errors: Optional[list] = None


# ============================================================
# ROOM SEARCH RESPONSE
# ============================================================

class RoomSearchResponse(BaseModel):

    success: bool

    message: str

    data: RoomListData

    errors: Optional[list] = None


# ============================================================
# ROOM COUNT DATA
# ============================================================

class RoomCountData(BaseModel):

    total_rooms: int = Field(
        ...,
        ge=0,
    )


# ============================================================
# ROOM COUNT RESPONSE
# ============================================================

class RoomCountResponse(BaseModel):

    success: bool

    message: str

    data: RoomCountData

    errors: Optional[list] = None