"""
システム設定API

メタデータ駆動: システム設定値はDB（system_settings）で管理
"""
import logging
import sys
from typing import Optional
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parents[5]))
from shared.database import READatabase

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
async def get_settings():
    """
    全設定一覧を取得

    値はマスキングして返却（セキュリティ対策）
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT key, value, description, is_encrypted, updated_at
            FROM system_settings
            ORDER BY key
        """)
        rows = cur.fetchall()

        settings_list = []
        for row in rows:
            key, value, description, is_encrypted, updated_at = row
            settings_list.append(SettingResponse(
                key=key,
                value=mask_value(value) if value else None,
                description=description,
                is_set=value is not None and value != '',
                updated_at=updated_at
            ))

        return settings_list
    except Exception as e:
        logger.error(f"設定取得エラー: {e}")
        raise HTTPException(status_code=500, detail="設定の取得に失敗しました")
    finally:
        cur.close()
        conn.close()


@router.get("/{key}")
async def get_setting(key: str):
    """
    特定の設定を取得

    値はマスキングして返却
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT key, value, description, is_encrypted, updated_at
            FROM system_settings
            WHERE key = %s
        """, (key,))
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"設定 '{key}' が見つかりません")

        key_val, value, description, is_encrypted, updated_at = row
        return SettingResponse(
            key=key_val,
            value=mask_value(value) if value else None,
            description=description,
            is_set=value is not None and value != '',
            updated_at=updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"設定取得エラー ({key}): {e}")
        raise HTTPException(status_code=500, detail="設定の取得に失敗しました")
    finally:
        cur.close()
        conn.close()


@router.put("/{key}")
async def update_setting(key: str, request: SettingUpdateRequest):
    """
    設定を更新

    存在しないキーの場合は404を返す
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # 存在確認
        cur.execute("SELECT key FROM system_settings WHERE key = %s", (key,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail=f"設定 '{key}' が見つかりません")

        # 更新
        cur.execute("""
            UPDATE system_settings
            SET value = %s, updated_at = NOW()
            WHERE key = %s
        """, (request.value, key))
        conn.commit()

        logger.info(f"設定更新: {key}")

        return {"message": "設定を更新しました", "key": key}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"設定更新エラー ({key}): {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail="設定の更新に失敗しました")
    finally:
        cur.close()
        conn.close()
