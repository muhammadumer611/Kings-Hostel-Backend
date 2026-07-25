from datetime import datetime, UTC

from firebase_admin import auth

from app.config.settings import settings
from app.repositories.auth_repository import AuthRepository
from app.utils.api_response import APIResponse
from app.utils.jwt_handler import create_access_token
from app.utils.logger import logger


class AuthService:

    def __init__(self):
        self.repository = AuthRepository()

    def create_default_admin(
        self,
        email: str,
        password: str,
    ):
        admin = self.repository.get_admin_by_email(email)

        if admin:
            logger.warning(f"Admin already exists: {email}")
            return APIResponse.error("Admin already exists.")

        self.repository.create_admin(
            email,
            password,
        )

        logger.info(f"Admin created successfully: {email}")

        return APIResponse.success("Admin created successfully.")

    def authenticate_admin(
        self,
        id_token: str,
    ):
        try:
            # Verify Firebase ID Token
            decoded_token = auth.verify_id_token(id_token)

            email = decoded_token.get("email")

            if not email:
                return APIResponse.error("Invalid authentication token.")

            admin = self.repository.verify_admin(email)

            if not admin:
                return APIResponse.error("You are not authorized.")

            if not admin.get("is_active"):
                return APIResponse.error("Your account has been disabled.")

            self.repository.update_last_login(
                admin["uid"],
                datetime.now(UTC),
            )

            token = create_access_token(
                {
                    "sub": admin["email"],
                    "uid": admin["uid"],
                    "role": admin["role"],
                }
            )

            logger.info(f"Admin logged in successfully: {email}")

            return APIResponse.success(
                "Login successful.",
                {
                    "access_token": token,
                    "token_type": "bearer",
                    "expires_in": (
                        settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
                    ),
                },
            )

        except Exception as e:
            logger.exception("Authentication failed.")
            return APIResponse.error(
                "Authentication failed.",
                str(e),
            )

    def get_profile(
        self,
        uid: str,
    ):
        try:
            profile = self.repository.get_admin_profile(uid)

            if not profile:
                return APIResponse.error("Admin not found.")

            return APIResponse.success(
                "Profile retrieved successfully.",
                profile,
            )

        except Exception as e:
            logger.exception("Failed to fetch profile.")
            return APIResponse.error(
                "Unable to fetch profile.",
                str(e),
            )

    def change_password(
        self,
        uid: str,
        current_password: str,
        new_password: str,
        confirm_password: str,
    ):
        try:
            if new_password != confirm_password:
                return APIResponse.error(
                    "New password and confirm password do not match."
                )

            self.repository.update_password(
                uid,
                new_password,
            )

            logger.info(f"Password changed successfully: {uid}")

            return APIResponse.success("Password updated successfully.")

        except Exception as e:
            logger.exception("Password update failed.")
            return APIResponse.error(
                "Unable to update password.",
                str(e),
            )

    def change_email(
        self,
        uid: str,
        current_password: str,
        new_email: str,
    ):
        try:
            admin = self.repository.get_admin_profile(uid)

            if not admin:
                return APIResponse.error("Admin not found.")

            self.repository.update_email(
                uid,
                new_email,
            )

            logger.info(f"Email updated successfully: {uid}")

            return APIResponse.success("Email updated successfully.")

        except Exception as e:
            logger.exception("Email update failed.")
            return APIResponse.error(
                "Unable to update email.",
                str(e),
            )

    def forgot_password(
        self,
        email: str,
    ):
        try:
            admin = self.repository.verify_admin(email)

            if not admin:
                return APIResponse.error("Admin account not found.")

            auth.generate_password_reset_link(email)

            logger.info(f"Password reset email sent: {email}")

            return APIResponse.success(
                "Password reset email sent successfully."
            )

        except Exception as e:
            logger.exception("Failed to send password reset email.")
            return APIResponse.error(
                "Unable to send password reset email.",
                str(e),
            )