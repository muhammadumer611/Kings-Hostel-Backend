from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field


class LoginRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    id_token: str = Field(
        ...,
        description="Firebase ID Token",
        examples=[
            "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
        ],
    )
class LoginData(BaseModel):

    access_token: str

    token_type: str

    expires_in: int


class LoginResponse(BaseModel):

    success: bool

    message: str

    data: LoginData

    errors: Optional[list] = None


class AdminProfile(BaseModel):

    uid: str

    full_name: str

    email: EmailStr

    phone: Optional[str] = None

    role: str

    is_active: bool

    profile_image: Optional[str] = None


class ProfileResponse(BaseModel):

    success: bool

    message: str

    data: AdminProfile

    errors: Optional[list] = None


class ChangePasswordRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    current_password: str

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
    )

    confirm_password: str


class ChangeEmailRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    current_password: str

    new_email: EmailStr


class ForgotPasswordRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    email: EmailStr



