from app.config.settings import settings
from app.repositories.auth_repository import AuthRepository
from app.utils.jwt_handler import create_access_token


class AuthService:

    def __init__(self):
        self.repository = AuthRepository()

    def create_default_admin(self, email, password):
        admin = self.repository.get_admin_by_email(email)

        if admin:
            return "Admin already exists."

        self.repository.create_admin(email, password)
        return "Admin created successfully."

    def authenticate_admin(self, email: str, password: str):
        normalized_email = (email or "").strip().lower()
        expected_email = (settings.ADMIN_EMAIL or "").strip().lower()

        if normalized_email == expected_email and password == settings.ADMIN_PASSWORD:
            token = create_access_token({"sub": normalized_email, "role": "super_admin"})
            return {
                "success": True,
                "message": "Login successful.",
                "data": {
                    "access_token": token,
                    "token_type": "bearer",
                },
                "errors": None,
            }

        return {
            "success": False,
            "message": "Invalid email or password.",
            "data": None,
            "errors": None,
        }