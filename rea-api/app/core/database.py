"""
REA API データベース接続
shared/database.pyを使用して統一管理
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# プロジェクトルートの.envを読み込む（shared/database.pyと同じ）
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

# 環境変数から接続情報を取得
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "real_estate_db")
DB_USER = os.getenv("DB_USER", "rea_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rea_password")

# SQLAlchemy用の接続文字列
db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy設定
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    """FastAPI依存性注入用"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# shared/database.pyからメソッドをインポート
from shared.database import READatabase

# 共通ライブラリのメソッドをエクスポート
get_connection = READatabase.get_connection
test_connection = READatabase.test_connection
execute_query = READatabase.execute_query
execute_query_dict = READatabase.execute_query_dict
