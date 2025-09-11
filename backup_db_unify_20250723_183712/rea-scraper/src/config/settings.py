"""
REA Scraper 設定管理
汎用学習スクレイピングシステムの設定を一元管理
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from loguru import logger

# .envファイルを読み込み
load_dotenv()

# プロジェクトのルートパス
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"
DOWNLOADS_DIR = BASE_DIR / "downloads"

# ディレクトリが存在しない場合は作成
for dir_path in [DATA_DIR, LOGS_DIR, MODELS_DIR, DOWNLOADS_DIR]:
    dir_path.mkdir(exist_ok=True)


class Settings:
    """設定クラス"""

    # =========== データベース設定 ===========
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/real_estate_db",  # ← ここだけ変更
    )

    # =========== Redis設定 ===========
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = 3600  # キャッシュの有効期限（秒）

    # =========== Selenium設定 ===========
    CHROME_DRIVER_PATH: Optional[str] = os.getenv("CHROME_DRIVER_PATH")
    HEADLESS_MODE: bool = os.getenv("HEADLESS_MODE", "False").lower() == "true"
    WINDOW_SIZE: tuple = (1920, 1080)
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # =========== スクレイピング設定 ===========
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30"))
    RETRY_COUNT: int = int(os.getenv("RETRY_COUNT", "3"))
    RETRY_DELAY: int = 5  # リトライ間隔（秒）
    RATE_LIMIT_DELAY: float = float(os.getenv("RATE_LIMIT_DELAY", "2"))
    MAX_CONCURRENT_REQUESTS: int = 3  # 同時リクエスト数

    # =========== ログ設定 ===========
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", str(LOGS_DIR / "rea_scraper.log"))
    LOG_ROTATION: str = "10 MB"  # ログローテーション
    LOG_RETENTION: str = "30 days"  # ログ保持期間
    LOG_FORMAT: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # =========== API設定 ===========
    REA_API_URL: str = os.getenv("REA_API_URL", "http://localhost:8005")
    API_TIMEOUT: int = 30
    API_KEY: Optional[str] = os.getenv("API_KEY")

    # =========== 汎用学習設定 ===========
    # 学習モード
    LEARNING_MODE: bool = True
    MIN_CONFIDENCE_THRESHOLD: float = 0.7  # 最小信頼度閾値

    # パターン学習設定
    PATTERN_MIN_SAMPLES: int = 10  # パターン学習に必要な最小サンプル数
    PATTERN_SIMILARITY_THRESHOLD: float = 0.8  # パターン類似度閾値

    # 品質評価設定
    QUALITY_CHECK_ENABLED: bool = True
    QUALITY_MIN_SCORE: float = 0.6  # 最小品質スコア

    # モデル保存設定
    MODEL_SAVE_INTERVAL: int = 100  # モデル保存間隔（処理件数）
    MODEL_VERSION_CONTROL: bool = True  # モデルのバージョン管理

    # =========== サイト別設定 ===========
    SITE_CONFIGS: Dict[str, Dict[str, Any]] = {
        "homes": {
            "base_url": "https://www.homes.co.jp",
            "rate_limit": 2.0,  # 秒
            "timeout": 30,
            "retry_count": 3,
            "priority": 1,  # 学習優先度
        },
        "suumo": {
            "base_url": "https://suumo.jp",
            "rate_limit": 2.5,
            "timeout": 30,
            "retry_count": 3,
            "priority": 2,
        },
        "athome": {
            "base_url": "https://www.athome.co.jp",
            "rate_limit": 3.0,
            "timeout": 30,
            "retry_count": 3,
            "priority": 3,
        },
    }

    # =========== 画像処理設定 ===========
    IMAGE_DOWNLOAD_ENABLED: bool = True
    IMAGE_MAX_SIZE: tuple = (1920, 1080)  # 最大画像サイズ
    IMAGE_QUALITY: int = 85  # JPEG品質
    IMAGE_FORMAT: str = "JPEG"

    # =========== スケジューラー設定 ===========
    SCHEDULER_ENABLED: bool = False
    SCHEDULER_TIMEZONE: str = "Asia/Tokyo"
    SCHEDULER_JOBS: list = [
        {
            "id": "daily_scraping",
            "func": "src.scheduler:daily_scraping_job",
            "trigger": "cron",
            "hour": 2,
            "minute": 0,
        },
    ]

    # =========== セキュリティ設定 ===========
    PROXY_ENABLED: bool = False
    PROXY_LIST: list = []
    ROTATE_USER_AGENT: bool = True
    USER_AGENT_LIST: list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    ]

    # =========== 開発/本番環境設定 ===========
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    @classmethod
    def get_site_config(cls, site_name: str) -> Dict[str, Any]:
        """サイト別設定を取得"""
        return cls.SITE_CONFIGS.get(site_name, {})

    @classmethod
    def validate(cls) -> None:
        """設定の妥当性をチェック"""
        # 必須ディレクトリの存在確認
        required_dirs = [DATA_DIR, LOGS_DIR, MODELS_DIR]
        for dir_path in required_dirs:
            if not dir_path.exists():
                raise ValueError(f"Required directory not found: {dir_path}")

        # データベース接続文字列の確認
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set")

        # API URLの確認
        if not cls.REA_API_URL:
            raise ValueError("REA_API_URL is not set")

        logger.info("Settings validation completed successfully")


# 設定インスタンス
settings = Settings()

# ログ設定の初期化
logger.add(
    settings.LOG_FILE,
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    backtrace=True,
    diagnose=True,
)

# 設定の検証（開発環境のみ）
if settings.DEBUG:
    try:
        settings.validate()
    except ValueError as e:
        logger.error(f"Settings validation failed: {e}")
        raise
