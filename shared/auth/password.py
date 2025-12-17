# パスワードハッシュ・検証
import bcrypt
from .config import AuthConfig


def hash_password(plain_password: str) -> str:
    """
    パスワードをハッシュ化

    Args:
        plain_password: 平文パスワード

    Returns:
        bcryptハッシュ文字列
    """
    salt = bcrypt.gensalt(rounds=AuthConfig.PASSWORD_HASH_ROUNDS)
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証

    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化されたパスワード

    Returns:
        一致すればTrue
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
