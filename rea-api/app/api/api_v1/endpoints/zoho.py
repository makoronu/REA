"""
ZOHO CRM 連携エンドポイント

リファクタリング: 2025-12-15
- コンテキストマネージャー使用
- カスタム例外使用
- 共通DB操作を関数化
"""
import json
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.core.exceptions import (
    ConfigurationError,
    DatabaseError,
    ExternalServiceError,
    ResourceNotFound,
)
from app.services.zoho.auth import zoho_auth
from app.services.zoho.client import zoho_client
from app.services.zoho.mapper import zoho_mapper, zoho_reverse_mapper
from shared.database import READatabase

router = APIRouter()


# ========================================
# スキーマ定義
# ========================================

class ZohoStatus(BaseModel):
    """ZOHO接続状態"""
    configured: bool
    has_refresh_token: bool
    connected: bool
    module_name: str
    module_exists: Optional[bool] = None
    error: Optional[str] = None


class ZohoAuthUrl(BaseModel):
    """OAuth認証URL"""
    auth_url: str


class ZohoImportRequest(BaseModel):
    """インポートリクエスト"""
    zoho_ids: List[str]
    update_existing: bool = True
    auto_geocode: bool = True


class ZohoImportResult(BaseModel):
    """インポート結果"""
    success: int
    failed: int
    skipped: int
    errors: List[dict]


# ========================================
# 共通ヘルパー関数
# ========================================

ALLOWED_RELATED_TABLES = {"land_info", "building_info"}


def _upsert_related_table(cur, table_name: str, property_id: int, data: dict):
    """関連テーブルの更新または挿入（共通処理）"""
    # SQLインジェクション対策: ホワイトリスト検証
    if table_name not in ALLOWED_RELATED_TABLES:
        raise ValueError(f"Table '{table_name}' is not allowed for upsert")

    if not data:
        return

    # road_info等のJSONフィールドを文字列化
    if "road_info" in data and isinstance(data["road_info"], (dict, list)):
        data["road_info"] = json.dumps(data["road_info"])

    # 既存レコードチェック
    cur.execute(f"SELECT id FROM {table_name} WHERE property_id = %s AND deleted_at IS NULL", (property_id,))
    existing = cur.fetchone()

    if existing:
        # UPDATE
        update_parts = [f"{col} = %s" for col in data.keys()]
        update_values = list(data.values()) + [property_id]
        cur.execute(
            f"UPDATE {table_name} SET {', '.join(update_parts)}, updated_at = NOW() WHERE property_id = %s",
            update_values
        )
    else:
        # INSERT
        data["property_id"] = property_id
        cols = list(data.keys())
        cur.execute(
            f"INSERT INTO {table_name} ({', '.join(cols)}, created_at, updated_at) VALUES ({', '.join(['%s']*len(cols))}, NOW(), NOW())",
            list(data.values())
        )


def _update_properties(cur, property_id: int, data: dict):
    """propertiesテーブルの更新"""
    if not data:
        return

    update_parts = []
    update_values = []
    for col, val in data.items():
        if col != "zoho_id":
            update_parts.append(f"{col} = %s")
            update_values.append(val)

    if update_parts:
        update_values.append(property_id)
        cur.execute(
            f"UPDATE properties SET {', '.join(update_parts)}, updated_at = NOW() WHERE id = %s",
            update_values
        )


def _insert_property(cur, data: dict) -> int:
    """propertiesテーブルに新規挿入"""
    cols = list(data.keys())
    cur.execute(
        f"INSERT INTO properties ({', '.join(cols)}, created_at, updated_at) VALUES ({', '.join(['%s']*len(cols))}, NOW(), NOW()) RETURNING id",
        list(data.values())
    )
    return cur.fetchone()[0]


def _update_staging_status(cur, conn, zoho_id: str, status: str, error_message: str = None):
    """stagingテーブルのステータス更新"""
    if status == 'success':
        cur.execute("""
            UPDATE zoho_import_staging
            SET import_status = 'success', imported_at = NOW(), error_message = NULL
            WHERE zoho_id = %s
        """, (zoho_id,))
    else:
        cur.execute("""
            UPDATE zoho_import_staging
            SET import_status = 'failed', error_message = %s
            WHERE zoho_id = %s
        """, (error_message, zoho_id))
    conn.commit()


# ========================================
# OAuth認証
# ========================================

@router.get("/auth", response_model=ZohoAuthUrl)
async def get_auth_url():
    """OAuth認証URLを取得"""
    if not zoho_auth.is_configured():
        raise ConfigurationError(
            "ZOHO認証情報が設定されていません。.envにZOHO_CLIENT_IDとZOHO_CLIENT_SECRETを設定してください。"
        )

    auth_url = zoho_auth.get_auth_url()
    return {"auth_url": auth_url}


@router.get("/callback")
async def oauth_callback(code: str = Query(...)):
    """OAuthコールバック - 認証コードをトークンに交換"""
    try:
        result = await zoho_auth.exchange_code_for_tokens(code)
        refresh_token = result.get("refresh_token", "")

        message = f"""
        <html>
        <head><meta charset="utf-8"><title>ZOHO認証成功</title></head>
        <body style="font-family: sans-serif; padding: 40px; max-width: 800px; margin: 0 auto;">
            <h1 style="color: #22c55e;">✅ ZOHO認証成功</h1>
            <p>以下のリフレッシュトークンを <code>.env</code> ファイルに設定してください：</p>
            <pre style="background: #f3f4f6; padding: 16px; border-radius: 8px; overflow-x: auto;">ZOHO_REFRESH_TOKEN={refresh_token}</pre>
            <p>設定後、FastAPIを再起動してください。</p>
            <p><a href="http://localhost:5173/import/zoho">インポート画面に戻る</a></p>
        </body>
        </html>
        """
        return HTMLResponse(content=message)

    except Exception as e:
        raise ExternalServiceError("ZOHO", f"トークン取得に失敗しました: {str(e)}")


# ========================================
# 接続状態確認
# ========================================

@router.get("/status", response_model=ZohoStatus)
async def get_status():
    """ZOHO接続状態を確認"""
    status = {
        "configured": zoho_auth.is_configured(),
        "has_refresh_token": zoho_auth.has_refresh_token(),
        "connected": False,
        "module_name": zoho_client.module_name,
        "module_exists": None,
        "error": None
    }

    if not status["configured"]:
        status["error"] = "認証情報が設定されていません"
        return status

    if not status["has_refresh_token"]:
        status["error"] = "リフレッシュトークンが設定されていません。OAuth認証を完了してください。"
        return status

    try:
        result = await zoho_client.test_connection()
        status["connected"] = result.get("success", False)
        status["module_exists"] = result.get("module_exists")
        if not result.get("success"):
            status["error"] = result.get("error")
    except Exception as e:
        status["error"] = str(e)

    return status


# ========================================
# モジュール・フィールド情報
# ========================================

@router.get("/modules")
async def get_modules():
    """利用可能なモジュール一覧を取得"""
    try:
        modules = await zoho_client.get_modules()
        return {"modules": modules}
    except Exception as e:
        raise ExternalServiceError("ZOHO", str(e))


@router.get("/fields")
async def get_fields(module: Optional[str] = None):
    """モジュールのフィールド一覧を取得"""
    try:
        fields = await zoho_client.get_fields(module)
        return {"fields": fields, "count": len(fields)}
    except Exception as e:
        raise ExternalServiceError("ZOHO", str(e))


# ========================================
# 物件データ取得
# ========================================

@router.get("/properties")
async def get_zoho_properties(
    page: int = 1,
    per_page: int = 50,
    criteria: Optional[str] = None
):
    """ZOHO CRMから物件一覧を取得"""
    try:
        result = await zoho_client.get_records(
            page=page,
            per_page=min(per_page, 200),
            criteria=criteria
        )
        return {
            "data": result.get("data", []),
            "info": result.get("info", {}),
            "page": page,
            "per_page": per_page
        }
    except Exception as e:
        raise ExternalServiceError("ZOHO", str(e))


@router.get("/properties/{zoho_id}")
async def get_zoho_property(zoho_id: str):
    """ZOHO CRMから特定の物件を取得"""
    try:
        record = await zoho_client.get_record(zoho_id)
        if not record:
            raise ResourceNotFound("ZOHO物件", zoho_id)
        return {"data": record}
    except ResourceNotFound:
        raise
    except Exception as e:
        raise ExternalServiceError("ZOHO", str(e))


# ========================================
# インポート機能
# ========================================

@router.post("/import", response_model=ZohoImportResult)
async def import_properties(request: ZohoImportRequest):
    """ZOHO CRMから物件をインポート（3テーブル対応）"""
    success_count = 0
    failed_count = 0
    skipped_count = 0
    errors = []

    with READatabase.cursor() as (cur, conn):
        for zoho_id in request.zoho_ids:
            try:
                # 1. ZOHOから物件データを取得
                zoho_record = await zoho_client.get_record(zoho_id)
                if not zoho_record:
                    errors.append({"zoho_id": zoho_id, "message": "物件が見つかりません"})
                    failed_count += 1
                    continue

                # 1.5. stagingテーブルに生データを保存
                cur.execute("""
                    INSERT INTO zoho_import_staging (zoho_id, raw_data, import_status)
                    VALUES (%s, %s, 'pending')
                    ON CONFLICT (zoho_id) DO UPDATE SET
                        raw_data = EXCLUDED.raw_data,
                        import_status = 'pending',
                        error_message = NULL,
                        created_at = NOW()
                """, (zoho_id, json.dumps(zoho_record)))
                conn.commit()

                # 2. データマッピングで変換（3テーブル分）
                rea_data = zoho_mapper.map_record(zoho_record)
                properties_data = rea_data["properties"]
                land_info_data = rea_data["land_info"]
                building_info_data = rea_data["building_info"]

                # 3. 既存物件チェック
                cur.execute("SELECT id FROM properties WHERE zoho_id = %s AND deleted_at IS NULL", (zoho_id,))
                existing = cur.fetchone()

                if existing:
                    if not request.update_existing:
                        skipped_count += 1
                        continue

                    property_id = existing[0]
                    _update_properties(cur, property_id, properties_data)
                    _upsert_related_table(cur, "land_info", property_id, land_info_data)
                    _upsert_related_table(cur, "building_info", property_id, building_info_data)
                else:
                    # 新規登録
                    property_id = _insert_property(cur, properties_data)
                    _upsert_related_table(cur, "land_info", property_id, land_info_data)
                    _upsert_related_table(cur, "building_info", property_id, building_info_data)

                # stagingテーブルのステータスを成功に更新
                _update_staging_status(cur, conn, zoho_id, 'success')
                success_count += 1

            except Exception as e:
                conn.rollback()
                try:
                    _update_staging_status(cur, conn, zoho_id, 'failed', str(e))
                except Exception as status_err:
                    logger.warning(f"Failed to update staging status: {status_err}")
                errors.append({"zoho_id": zoho_id, "message": str(e)})
                failed_count += 1

    return {
        "success": success_count,
        "failed": failed_count,
        "skipped": skipped_count,
        "errors": errors
    }


# ========================================
# Staging管理
# ========================================

@router.get("/staging/status")
async def get_staging_status():
    """stagingテーブルのステータス集計"""
    with READatabase.cursor() as (cur, conn):
        cur.execute("""
            SELECT import_status, COUNT(*)
            FROM zoho_import_staging
            WHERE deleted_at IS NULL
            GROUP BY import_status
        """)
        status_counts = {row[0]: row[1] for row in cur.fetchall()}

        cur.execute("SELECT COUNT(*) FROM zoho_import_staging WHERE deleted_at IS NULL")
        total = cur.fetchone()[0]

        return {
            "total": total,
            "pending": status_counts.get("pending", 0),
            "success": status_counts.get("success", 0),
            "failed": status_counts.get("failed", 0)
        }


@router.get("/staging/failed")
async def get_failed_records():
    """失敗レコード一覧"""
    with READatabase.cursor() as (cur, conn):
        cur.execute("""
            SELECT zoho_id, error_message, created_at,
                   raw_data->>'Name' as property_name
            FROM zoho_import_staging
            WHERE import_status = 'failed' AND deleted_at IS NULL
            ORDER BY created_at DESC
        """)
        failed = [
            {
                "zoho_id": row[0],
                "error_message": row[1],
                "created_at": str(row[2]) if row[2] else None,
                "property_name": row[3]
            }
            for row in cur.fetchall()
        ]
        return {"failed": failed, "count": len(failed)}


# ========================================
# REA → ZOHO 同期
# ========================================

class ZohoSyncRequest(BaseModel):
    """同期リクエスト"""
    property_ids: List[int]


class ZohoSyncResult(BaseModel):
    """同期結果"""
    success: int
    failed: int
    created: int
    updated: int
    errors: List[dict]


def _get_table_columns(cur, table_name: str) -> list:
    """テーブルのカラム一覧を取得"""
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    return [row[0] for row in cur.fetchall()]


def _get_property_full_data(cur, property_id: int) -> Optional[dict]:
    """物件の全データを取得（properties + land_info + building_info）"""
    # properties
    prop_columns = _get_table_columns(cur, "properties")
    prop_columns_str = ", ".join(prop_columns)
    cur.execute(f"SELECT {prop_columns_str} FROM properties WHERE id = %s AND deleted_at IS NULL", (property_id,))
    prop_row = cur.fetchone()
    if not prop_row:
        return None

    result = {"properties": dict(zip(prop_columns, prop_row))}

    # land_info
    land_columns = _get_table_columns(cur, "land_info")
    land_columns_str = ", ".join(land_columns)
    cur.execute(f"SELECT {land_columns_str} FROM land_info WHERE property_id = %s AND deleted_at IS NULL", (property_id,))
    land_row = cur.fetchone()
    if land_row:
        result["land_info"] = dict(zip(land_columns, land_row))
    else:
        result["land_info"] = {}

    # building_info
    building_columns = _get_table_columns(cur, "building_info")
    building_columns_str = ", ".join(building_columns)
    cur.execute(f"SELECT {building_columns_str} FROM building_info WHERE property_id = %s AND deleted_at IS NULL", (property_id,))
    building_row = cur.fetchone()
    if building_row:
        result["building_info"] = dict(zip(building_columns, building_row))
    else:
        result["building_info"] = {}

    return result


@router.post("/sync", response_model=ZohoSyncResult)
async def sync_to_zoho(request: ZohoSyncRequest):
    """REAの物件データをZOHOに同期（逆方向）"""
    success_count = 0
    failed_count = 0
    created_count = 0
    updated_count = 0
    errors = []

    with READatabase.cursor() as (cur, conn):
        for property_id in request.property_ids:
            try:
                # 1. REAから物件データ取得
                rea_data = _get_property_full_data(cur, property_id)
                if not rea_data:
                    errors.append({"property_id": property_id, "message": "物件が見つかりません"})
                    failed_count += 1
                    continue

                # 2. 逆マッピングでZOHO形式に変換
                zoho_data = zoho_reverse_mapper.reverse_map_record(rea_data)

                # 3. zoho_idの有無で更新/新規作成を判定
                zoho_id = rea_data["properties"].get("zoho_id")

                if zoho_id:
                    # 既存レコード更新
                    result = await zoho_client.update_record(zoho_id, zoho_data)
                    updated_count += 1
                else:
                    # 新規作成
                    result = await zoho_client.create_record(zoho_data)
                    # 作成されたzoho_idをREAに保存
                    if result.get("data") and len(result["data"]) > 0:
                        new_zoho_id = result["data"][0].get("details", {}).get("id")
                        if new_zoho_id:
                            cur.execute("""
                                UPDATE properties
                                SET zoho_id = %s, zoho_synced_at = NOW(), zoho_sync_status = 'synced'
                                WHERE id = %s
                            """, (str(new_zoho_id), property_id))
                            conn.commit()
                    created_count += 1

                # 同期日時更新
                cur.execute("""
                    UPDATE properties
                    SET zoho_synced_at = NOW(), zoho_sync_status = 'synced'
                    WHERE id = %s
                """, (property_id,))
                conn.commit()
                success_count += 1

            except Exception as e:
                conn.rollback()
                errors.append({"property_id": property_id, "message": str(e)})
                failed_count += 1

    return {
        "success": success_count,
        "failed": failed_count,
        "created": created_count,
        "updated": updated_count,
        "errors": errors
    }


@router.post("/sync/{property_id}")
async def sync_single_to_zoho(property_id: int):
    """単一物件をZOHOに同期"""
    request = ZohoSyncRequest(property_ids=[property_id])
    return await sync_to_zoho(request)


@router.post("/staging/retry")
async def retry_failed_imports():
    """失敗レコードをstagingの生データから再インポート"""
    success_count = 0
    failed_count = 0
    errors = []

    with READatabase.cursor() as (cur, conn):
        cur.execute("""
            SELECT zoho_id, raw_data
            FROM zoho_import_staging
            WHERE import_status = 'failed'
        """)
        failed_records = cur.fetchall()

        for zoho_id, raw_data in failed_records:
            try:
                zoho_record = raw_data if isinstance(raw_data, dict) else json.loads(raw_data)

                rea_data = zoho_mapper.map_record(zoho_record)
                properties_data = rea_data["properties"]
                land_info_data = rea_data["land_info"]
                building_info_data = rea_data["building_info"]

                cur.execute("SELECT id FROM properties WHERE zoho_id = %s AND deleted_at IS NULL", (zoho_id,))
                existing = cur.fetchone()

                if existing:
                    property_id = existing[0]
                    _update_properties(cur, property_id, properties_data)
                else:
                    property_id = _insert_property(cur, properties_data)
                    _upsert_related_table(cur, "land_info", property_id, land_info_data)
                    _upsert_related_table(cur, "building_info", property_id, building_info_data)

                _update_staging_status(cur, conn, zoho_id, 'success')
                success_count += 1

            except Exception as e:
                conn.rollback()
                _update_staging_status(cur, conn, zoho_id, 'failed', str(e))
                errors.append({"zoho_id": zoho_id, "message": str(e)})
                failed_count += 1

    return {
        "success": success_count,
        "failed": failed_count,
        "errors": errors
    }
