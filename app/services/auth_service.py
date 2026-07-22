from app.config.settings import settings
from app.repositories.auth_repository import AuthRepository

from app.utils.jwt_handler import create_access_token
from app.utils.password_handler import verify_password
from app.utils.api_response import APIResponse
from app.utils.logger import logger


class AuthService:

    def __init__(self):
        self.repository = AuthRepository()

    def create_default_admin(self, email: str, password: str):

        admin = self.repository.get_admin_by_email(email)

        if admin:

            logger.warning(
                f"Admin already exists: {email}"
            )

            return APIResponse.error(
                "Admin already exists."
            )

        self.repository.create_admin(email, password)

        logger.info(
            f"Admin created successfully: {email}"
        )

        return APIResponse.success(
            "Admin created successfully."
        )

    def authenticate_admin(
        self,
        email: str,
        password: str,
    ):

        try:

            normalized_email = (
                email or ""
            ).strip().lower()

            expected_email = (
                settings.ADMIN_EMAIL or ""
            ).strip().lower()

            # Email Check
            if normalized_email != expected_email:

                logger.warning(
                    f"Invalid login email: {email}"
                )

                return APIResponse.error(
                    "Invalid email or password."
                )

            # Password Check
            if not verify_password(
                password,
                settings.ADMIN_PASSWORD,
            ):

                logger.warning(
                    f"Invalid password attempt for: {email}"
                )

                return APIResponse.error(
                    "Invalid email or password."
                )

            # Generate JWT Token
            token = create_access_token(
                {
                    "sub": normalized_email,
                    "role": "super_admin",
                }
            )

            logger.info(
                f"Admin logged in successfully: {email}"
            )

            return APIResponse.success(
                "Login successful.",
                {
                    "access_token": token,
                    "token_type": "bearer",
                },
            )

        except Exception as e:

            logger.exception(
                f"Authentication failed: {str(e)}"
            )

            return APIResponse.error(
                "Authentication failed.",
                str(e),
            )