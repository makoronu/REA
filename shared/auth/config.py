# 認証設定（.envから読み込み）
import os
from dotenv import load_dotenv

load_dotenv()


class AuthConfig:
    """認証関連の設定値"""

    # JWT設定
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', '')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRE_MINUTES: int = int(os.getenv('JWT_EXPIRE_MINUTES', '60'))

    # パスワードハッシュ設定
    PASSWORD_HASH_ROUNDS: int = int(os.getenv('PASSWORD_HASH_ROUNDS', '12'))

    @classmethod
    def validate(cls) -> None:
        """必須設定のバリデーション"""
        if not cls.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY is required in .env")
        if len(cls.JWT_SECRET_KEY) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters")
