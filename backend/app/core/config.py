import json
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # API
    PROJECT_NAME: str = "ILMA Backend"
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_USER: str = "ilma_user"
    POSTGRES_PASSWORD: str = "ilma_password"
    POSTGRES_DB: str = "ilma_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = ""

    @model_validator(mode="after")
    def build_database_url(self):
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # SMS Provider (mock | twilio)
    SMS_PROVIDER: str = "mock"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""

    # Push Provider (mock | fcm)
    PUSH_PROVIDER: str = "mock"

    # Notification scheduler
    NOTIFICATIONS_ENABLED: bool = True
    NOTIFICATION_MAX_PER_DAY: int = 2

    # Payment Providers
    KKIAPAY_PUBLIC_KEY: str = ""
    KKIAPAY_PRIVATE_KEY: str = ""
    KKIAPAY_SECRET: str = ""
    FEDAPAY_API_KEY: str = ""
    FEDAPAY_ENVIRONMENT: str = "sandbox"

    # S3 / Minio
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "ilma_minio"
    S3_SECRET_KEY: str = "ilma_minio_secret"
    S3_BUCKET: str = "ilma-packs"
    S3_REGION: str = "us-east-1"

    # CORS
    BACKEND_CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173"]'

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return json.loads(self.BACKEND_CORS_ORIGINS)


settings = Settings()
