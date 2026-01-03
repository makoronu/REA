"""
日付フォーマットユーティリティ

ADR-0001に基づき、日付フォーマットを定数ファイルで一元管理。

メタデータ駆動ではなく定数化の理由:
- 開発者のみが変更
- 変更頻度が年1回以下
- 外部仕様（HOMES等）に依存
"""
from datetime import datetime, timedelta
from typing import Any, Optional


# 日付フォーマット定数
class DateFormats:
    """日付フォーマット定数"""

    # HOMES出力用
    HOMES_DATETIME = '%Y/%m/%d %H:%M:%S'
    HOMES_DATE = '%Y/%m/%d'
    HOMES_YYYYMM = '%Y/%m'

    # ファイル名用
    FILENAME = '%Y%m%d_%H%M%S'

    # 表示用
    DISPLAY_DATE = '%Y-%m-%d'
    DISPLAY_DATETIME = '%Y-%m-%d %H:%M:%S'


def format_datetime_homes(dt: Any) -> str:
    """日時をHOMES形式（yyyy/mm/dd hh:mm:ss）に変換"""
    if dt is None:
        return datetime.now().strftime(DateFormats.HOMES_DATETIME)
    if isinstance(dt, str):
        return dt
    return dt.strftime(DateFormats.HOMES_DATETIME)


def format_date_homes(dt: Any, default_days: int = 14) -> str:
    """日付をHOMES形式（yyyy/mm/dd）に変換"""
    if dt is None:
        return (datetime.now() + timedelta(days=default_days)).strftime(DateFormats.HOMES_DATE)
    if isinstance(dt, str):
        return dt
    return dt.strftime(DateFormats.HOMES_DATE)


def format_yyyymm_homes(dt: Any) -> str:
    """日付をHOMES形式（yyyy/mm）に変換"""
    if dt is None:
        return ""
    if isinstance(dt, str):
        return dt[:7].replace('-', '/')
    return dt.strftime(DateFormats.HOMES_YYYYMM)


def format_filename_timestamp() -> str:
    """ファイル名用タイムスタンプを生成"""
    return datetime.now().strftime(DateFormats.FILENAME)
