# FastAPI認証ミドルウェア
from functools import wraps
from typing import Optional
from fastapi import Request, HTTPException
from .jwt_handler import verify_token


def get_current_user(request: Request) -> Optional[dict]:
    """
    リクエストからユーザー情報を取得

    Args:
        request: FastAPIリクエスト

    Returns:
        ユーザー情報またはNone
    """
    # Authorizationヘッダーから取得
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    # Bearer token形式をチェック
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None

    token = parts[1]
    return verify_token(token)


def require_auth(min_level: int = 0):
    """
    認証・認可デコレータ

    Args:
        min_level: 必要な最小権限レベル（デフォルト: 0 = ログインのみ）

    Usage:
        @app.get("/api/v1/properties")
        @require_auth()
        async def get_properties(request: Request):
            user = request.state.current_user
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # 1. JWT検証
            user = get_current_user(request)
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="認証が必要です"
                )

            # 2. 権限レベルチェック
            user_level = user.get('role_level', 0)
            if user_level < min_level:
                raise HTTPException(
                    status_code=403,
                    detail="権限が不足しています"
                )

            # 3. リクエストにユーザー情報を付与
            request.state.current_user = user

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_super_admin():
    """super_admin専用（level: 100）"""
    return require_auth(min_level=100)


def require_admin():
    """admin以上（level: 50）"""
    return require_auth(min_level=50)


def require_user():
    """一般ユーザー以上（level: 10）"""
    return require_auth(min_level=10)
