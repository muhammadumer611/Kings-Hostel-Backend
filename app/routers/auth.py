from fastapi import APIRouter, Depends

from app.dependencies.auth_dependency import get_current_admin
from app.services.auth_service import AuthService
from app.schemas.auth_schema import (
    LoginRequest,
    ChangePasswordRequest,
    ChangeEmailRequest,
    ForgotPasswordRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.get("/")
def auth_home():
    return {"message": "Authentication API Working"}


@router.post("/login")
def login(payload: LoginRequest):
    return auth_service.authenticate_admin(payload.id_token)


@router.get("/me")
def get_current_user(
    current_admin=Depends(get_current_admin),
):
    return auth_service.get_profile(
        current_admin["uid"],
    )


@router.put("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_admin=Depends(get_current_admin),
):
    return auth_service.change_password(
    current_admin["uid"],
    payload.current_password,
    payload.new_password,
    payload.confirm_password,
)


@router.put("/change-email")
def change_email(
    payload: ChangeEmailRequest,
    current_admin=Depends(get_current_admin),
):
    return auth_service.change_email(
    current_admin["uid"],
    payload.current_password,
    payload.new_email,
)
@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
):
    return auth_service.forgot_password(
        payload.email,
    )


@router.post("/logout")
def logout():
    return {
        "success": True,
        "message": "Logout successful.",
        "data": None,
        "errors": None,
    }