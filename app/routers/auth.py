from fastapi import APIRouter, Depends
from app.dependencies.auth_dependency import get_current_admin
from app.schemas.auth_schema import LoginRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.get("/")
def auth_home():
    return {
        "message": "Authentication API Working"
    }


@router.post("/login")
def login(payload: LoginRequest):
    return auth_service.authenticate_admin(payload.email, payload.password)


@router.get("/me")
def get_current_user(payload=Depends(get_current_admin)):
    return {
        "success": True,
        "message": "Profile retrieved successfully.",
        "data": {
            "email": payload.get("sub"),
            "role": payload.get("role"),
        },
        "errors": None,
    }