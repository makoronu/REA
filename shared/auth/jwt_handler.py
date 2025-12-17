# JWT発行・検証
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from .config import AuthConfig


def create_token(payload: dict) -> str:
    """
    JWTトークンを発行

    Args:
        payload: トークンに含めるデータ
            - user_id: int
            - organization_id: int
            - role_code: str
            - role_level: int

    Returns:
        JWTトークン文字列
    """
    AuthConfig.validate()

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=AuthConfig.JWT_EXPIRE_MINUTES)

    token_payload = {
        **payload,
        'iat': now,
        'exp': expire,
    }

    return jwt.encode(
        token_payload,
        AuthConfig.JWT_SECRET_KEY,
        algorithm=AuthConfig.JWT_ALGORITHM
    )


def verify_token(token: str) -> Optional[dict]:
    """
    JWTトークンを検証

    Args:
        token: JWTトークン文字列

    Returns:
        検証成功時はペイロード、失敗時はNone
    """
    AuthConfig.validate()

    try:
        payload = jwt.decode(
            token,
            AuthConfig.JWT_SECRET_KEY,
            algorithms=[AuthConfig.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
