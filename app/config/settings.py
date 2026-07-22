from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Kings Hostel Backend"
    VERSION: str = "1.0.0"

    ADMIN_EMAIL: str = "admin@kingshostel.com"
    ADMIN_PASSWORD: str = "admin123"

    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()