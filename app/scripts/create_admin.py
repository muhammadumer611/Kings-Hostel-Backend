from app.config.settings import settings
from app.services.auth_service import AuthService
from app.utils.logger import logger


def main():

    auth_service = AuthService()

    result = auth_service.create_default_admin(
        settings.ADMIN_EMAIL,
        settings.ADMIN_PASSWORD
    )

    logger.info(result)


if __name__ == "__main__":
    main()