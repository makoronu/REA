import os
from pathlib import Path

from pydantic_settings import BaseSettings

# .envファイルパス（本番: /opt/REA/.env、ローカル: プロジェクトルート）
_ENV_FILE = "/opt/REA/.env" if Path("/opt/REA/.env").exists() else str(Path(__file__).parents[2] / ".env")


class GeoSettings(BaseSettings):
    PROJECT_NAME: str = "REA Geo API"

    # 外部API URL設定
    GSI_GEOCODE_URL: str = "https://msearch.gsi.go.jp/address-search/AddressSearch"
    NOMINATIM_GEOCODE_URL: str = "https://nominatim.openstreetmap.org/search"
    GOOGLE_GEOCODE_URL: str = "https://maps.googleapis.com/maps/api/geocode/json"

    # Google Maps API（ジオコーディング用）
    GOOGLE_MAPS_API_KEY: str | None = os.getenv("GOOGLE_MAPS_API_KEY")

    class Config:
        env_file = _ENV_FILE
        case_sensitive = True
        extra = "allow"


settings = GeoSettings()
