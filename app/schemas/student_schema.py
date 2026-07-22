from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class StudentPersonal(BaseModel):
    name: str = Field(..., min_length=2)
    cnic: str = Field(..., min_length=5)
    phone: str = Field(..., min_length=11)
    email: EmailStr
    bloodGroup: Optional[str] = None


class StudentGuardian(BaseModel):
    name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=11)
    cnic: str = Field(..., min_length=5)


class StudentAllocation(BaseModel):
    block: str = Field(..., min_length=1)
    roomType: str = Field(..., min_length=1)


class StudentCreate(BaseModel):
    personal: StudentPersonal
    guardian: StudentGuardian
    allocation: StudentAllocation
    status: Optional[str] = "Active"