import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.api_v1.api import api_router
from .core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="REA - Real Estate Automation API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では具体的なドメインを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル（画像アップロード用）
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# API ルーター
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "REA - Real Estate Automation API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
