"""
REA Scraper ログ管理
ログの設定、カスタムハンドラー、ログユーティリティ
"""
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger
from src.config.settings import settings

# ログディレクトリの作成
log_dir = Path(settings.LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)


def setup_logger():
    """ログの初期設定"""
    # 既存のハンドラーを削除
    logger.remove()

    # コンソール出力（開発用）
    if settings.DEBUG:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>",
            level=settings.LOG_LEVEL,
            colorize=True,
        )
    else:
        # 本番環境では簡潔なフォーマット
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="INFO",
        )

    # ファイル出力（全ログ）
    logger.add(
        settings.LOG_FILE,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8",
    )

    # エラーログ専用ファイル
    error_log_file = log_dir / "errors.log"
    logger.add(
        error_log_file,
        format=settings.LOG_FORMAT,
        level="ERROR",
        rotation="1 week",
        retention="1 month",
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8",
    )

    # 物件取得ログ（成功した物件の記録）
    property_log_file = log_dir / "properties.log"
    logger.add(
        property_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        level="SUCCESS",
        filter=lambda record: "property_saved" in record["extra"],
        rotation="1 day",
        retention="1 week",
        encoding="utf-8",
    )

    logger.info("Logger initialized successfully")


# 初期化実行
setup_logger()


# カスタムログ関数
def log_property_saved(property_data: Dict[str, Any]):
    """保存された物件をログ記録"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "title": property_data.get("title", "No title"),
        "price": property_data.get("price", 0),
        "address": property_data.get("address", ""),
        "contractor_company_name": property_data.get("contractor_company_name", ""),
        "source_site": property_data.get("source_site", ""),
        "listing_id": property_data.get("listing_id", ""),
    }

    logger.bind(property_saved=True).success(
        f"Property saved: {json.dumps(log_data, ensure_ascii=False)}"
    )


def log_scraping_stats(site_name: str, stats: Dict[str, Any]):
    """スクレイピング統計をログ記録"""
    logger.info(
        f"""
    Scraping statistics for {site_name}:
    - Total pages: {stats.get('pages_scraped', 0)}
    - Properties found: {stats.get('properties_found', 0)}
    - Properties saved: {stats.get('properties_saved', 0)}
    - Errors: {stats.get('errors', 0)}
    - Duration: {stats.get('duration', 0):.1f} seconds
    - Success rate: {stats.get('success_rate', 0):.1%}
    """
    )


def log_error_with_context(error: Exception, context: Dict[str, Any]):
    """エラーをコンテキスト付きでログ記録"""
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "context": context,
        "timestamp": datetime.now().isoformat(),
    }

    logger.error(
        f"Error occurred: {json.dumps(error_data, ensure_ascii=False, indent=2)}"
    )


def log_learning_progress(site_name: str, learning_data: Dict[str, Any]):
    """学習進捗をログ記録"""
    logger.info(
        f"""
    Learning progress for {site_name}:
    - Successful selectors: {len(learning_data.get('successful_selectors', {}))}
    - Failed selectors: {len(learning_data.get('failed_selectors', {}))}
    - Patterns found: {len(learning_data.get('patterns_found', {}))}
    - Sample data collected: {len(learning_data.get('sample_data', []))}
    - Success rate: {learning_data.get('success_rate', 0):.1%}
    """
    )


# デコレータ
def log_execution_time(func):
    """関数の実行時間をログ記録するデコレータ"""
    import functools
    import time

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.2f} seconds: {e}"
            )
            raise

    return wrapper


def log_api_call(endpoint: str, params: Optional[Dict[str, Any]] = None):
    """API呼び出しをログ記録"""
    logger.info(f"API call: {endpoint} with params: {params or {}}")


def log_database_operation(operation: str, table: str, record_count: int):
    """データベース操作をログ記録"""
    logger.info(f"Database {operation} on {table}: {record_count} records")


# スクレイピング専用ログ
class ScrapingLogger:
    """スクレイピング処理専用のログクラス"""

    def __init__(self, site_name: str):
        self.site_name = site_name
        self.start_time = datetime.now()
        self.stats = {
            "pages_scraped": 0,
            "properties_found": 0,
            "properties_saved": 0,
            "errors": 0,
        }

    def log_page_start(self, url: str):
        """ページ処理開始をログ"""
        logger.info(f"[{self.site_name}] Starting to scrape: {url}")

    def log_page_complete(self, url: str, property_count: int):
        """ページ処理完了をログ"""
        self.stats["pages_scraped"] += 1
        self.stats["properties_found"] += property_count
        logger.info(
            f"[{self.site_name}] Completed scraping {url}: "
            f"found {property_count} properties"
        )

    def log_property_saved(self, property_data: Dict[str, Any]):
        """物件保存をログ"""
        self.stats["properties_saved"] += 1
        log_property_saved(property_data)

    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """エラーをログ"""
        self.stats["errors"] += 1
        log_error_with_context(error, context or {})

    def log_completion(self):
        """処理完了をログ"""
        duration = (datetime.now() - self.start_time).total_seconds()
        self.stats["duration"] = duration

        if self.stats["properties_found"] > 0:
            self.stats["success_rate"] = (
                self.stats["properties_saved"] / self.stats["properties_found"]
            )
        else:
            self.stats["success_rate"] = 0

        log_scraping_stats(self.site_name, self.stats)


# エクスポート
__all__ = [
    "logger",
    "setup_logger",
    "log_property_saved",
    "log_scraping_stats",
    "log_error_with_context",
    "log_learning_progress",
    "log_execution_time",
    "log_api_call",
    "log_database_operation",
    "ScrapingLogger",
]
