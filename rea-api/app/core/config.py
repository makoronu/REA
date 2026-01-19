import os
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
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # ファイルアップロード
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_FILE_SIZE: Optional[int] = 10 * 1024 * 1024  # 10MB - 環境変数から来る可能性がある
    UPLOAD_DIR: str = "uploads"

    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",  # Vite開発サーバー用
    ]

    # ログ設定
    LOG_LEVEL: str = "INFO"

    # 外部API URL設定（ハードコード回避）
    ZOHO_AUTH_URL: str = "https://accounts.zoho.jp/oauth/v2/auth"
    ZOHO_TOKEN_URL: str = "https://accounts.zoho.jp/oauth/v2/token"
    ZOHO_API_DOMAIN: str = "https://www.zohoapis.jp"
    REINFOLIB_BASE_URL: str = "https://www.reinfolib.mlit.go.jp/ex-api/external"
    GSI_GEOCODE_URL: str = "https://msearch.gsi.go.jp/address-search/AddressSearch"
    NOMINATIM_GEOCODE_URL: str = "https://nominatim.openstreetmap.org/search"
    GOOGLE_GEOCODE_URL: str = "https://maps.googleapis.com/maps/api/geocode/json"

    # Google Maps API（ジオコーディング用）
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # 追加の環境変数を許可


settings = Settings()
