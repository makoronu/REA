"""
システム設定API

メタデータ駆動: システム設定値はDB（system_settings）で管理
"""
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text

from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class SettingResponse(BaseModel):
    """設定取得レスポンス"""
    key: str
    value: Optional[str]  # マスク済みの値
    description: Optional[str]
    is_set: bool  # 値が設定されているか
    updated_at: Optional[datetime]


class SettingUpdateRequest(BaseModel):
    """設定更新リクエスト"""
    value: str


def mask_value(value: Optional[str]) -> Optional[str]:
    """値をマスキング（最初の4文字以外を*に）"""
    if not value:
        return None
    if len(value) <= 4:
        return '*' * len(value)
    return value[:4] + '*' * (len(value) - 4)


@router.get("/")
async def get_settings(db=Depends(get_db)):
    """
    全設定一覧を取得

    値はマスキングして返却（セキュリティ対策）
    """
    try:
        result = db.execute(text("""
            SELECT key, value, description, is_encrypted, updated_at
            FROM system_settings
            ORDER BY key
        """))
        rows = result.fetchall()

        settings = []
        for row in rows:
            settings.append(SettingResponse(
                key=row.key,
                value=mask_value(row.value) if row.value else None,
                description=row.description,
                is_set=row.value is not None and row.value != '',
                updated_at=row.updated_at
            ))

        return settings
    except Exception as e:
        logger.error(f"設定取得エラー: {e}")
        raise HTTPException(status_code=500, detail="設定の取得に失敗しました")


@router.get("/{key}")
async def get_setting(key: str, db=Depends(get_db)):
    """
    特定の設定を取得

    値はマスキングして返却
    """
    try:
        result = db.execute(text("""
            SELECT key, value, description, is_encrypted, updated_at
            FROM system_settings
            WHERE key = :key
        """), {"key": key})
        row = result.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"設定 '{key}' が見つかりません")

        return SettingResponse(
            key=row.key,
            value=mask_value(row.value) if row.value else None,
            description=row.description,
            is_set=row.value is not None and row.value != '',
            updated_at=row.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"設定取得エラー ({key}): {e}")
        raise HTTPException(status_code=500, detail="設定の取得に失敗しました")


@router.put("/{key}")
async def update_setting(key: str, request: SettingUpdateRequest, db=Depends(get_db)):
    """
    設定を更新

    存在しないキーの場合は404を返す
    """
    try:
        # 存在確認
        check = db.execute(text("""
            SELECT key FROM system_settings WHERE key = :key
        """), {"key": key})
        if not check.fetchone():
            raise HTTPException(status_code=404, detail=f"設定 '{key}' が見つかりません")

        # 更新
        db.execute(text("""
            UPDATE system_settings
            SET value = :value, updated_at = NOW()
            WHERE key = :key
        """), {"key": key, "value": request.value})
        db.commit()

        logger.info(f"設定更新: {key}")

        return {"message": "設定を更新しました", "key": key}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"設定更新エラー ({key}): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="設定の更新に失敗しました")


def get_setting_value(db, key: str) -> Optional[str]:
    """
    設定値を取得（内部API用、マスクなし）

    geo.py等から呼び出される
    """
    try:
        result = db.execute(text("""
            SELECT value FROM system_settings WHERE key = :key
        """), {"key": key})
        row = result.fetchone()
        return row.value if row else None
    except Exception as e:
        logger.error(f"設定値取得エラー ({key}): {e}")
        return None
