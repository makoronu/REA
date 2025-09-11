from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API設定
    PROJECT_NAME: str = "REA API"
    API_V1_STR: str = "/api/v1"

    # セキュリティ
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # データベース
    DATABASE_URL: str = "postgresql://rea_user:rea_password@localhost/real_estate_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # ファイルアップロード
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # ログ設定
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
