"""
REA Geo API - 地理情報サービス（読み取り専用）

Core APIから分離した地理情報専用サービス。
PostGISを使用した空間検索を提供。
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .endpoints import geo

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="REA Geo API - 地理情報サービス（読み取り専用）",
    openapi_url="/api/v1/geo/openapi.json",
)

# CORS設定（Core APIと同一）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://realestateautomation.net",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Geoルーター登録
app.include_router(geo.router, prefix="/api/v1/geo", tags=["geo"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "geo"}
