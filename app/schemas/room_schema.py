from typing import List, Optional
from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    room_number: str = Field(..., min_length=1)
    block: str = Field(..., min_length=1)
    floor: int = Field(..., ge=0)
    room_type: str = Field(..., min_length=1)
    total_beds: int = Field(..., ge=1)
    occupied_beds: int = Field(default=0, ge=0)
    status: str = "Available"
    price_per_month: float = Field(default=0.0, ge=0)
    security_deposit: float = Field(default=0.0, ge=0)
    amenities: Optional[List[str]] = None


class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    block: Optional[str] = None
    floor: Optional[int] = None
    room_type: Optional[str] = None
    total_beds: Optional[int] = None
    occupied_beds: Optional[int] = None
    status: Optional[str] = None
    price_per_month: Optional[float] = None
    security_deposit: Optional[float] = None
    amenities: Optional[List[str]] = None
