import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.api_v1.api import api_router
from .core.config import settings
from .core.exceptions import REAException

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


# カスタム例外ハンドラー
@app.exception_handler(REAException)
async def rea_exception_handler(request: Request, exc: REAException):
    """REAカスタム例外を統一的にハンドリング"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, **exc.extra}
    )
