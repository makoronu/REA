# TODO: 実装予定
"""
API依存関係の定義
主にデータベースセッションの管理
"""
from typing import Generator

from app.core.database import SessionLocal
from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションを生成する
    リクエスト完了後に自動的にクローズされる
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
