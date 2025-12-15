"""
外部連携管理エンドポイント

連携先マスター（m_integrations）の管理と、
物件の同期状態確認・一括同期を行う。
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from shared.database import READatabase

router = APIRouter()


# ========================================
# スキーマ定義
# ========================================

class Integration(BaseModel):
    """連携先"""
    id: int
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool
    sync_endpoint: Optional[str] = None
    icon_class: Optional[str] = None


class IntegrationUpdate(BaseModel):
    """連携先更新"""
    is_active: bool


class PropertySyncStatus(BaseModel):
    """物件の同期状態"""
    property_id: int
    property_name: Optional[str] = None
    integrations: dict  # {code: {synced: bool, synced_at: str, external_id: str}}


class BulkSyncRequest(BaseModel):
    """一括同期リクエスト"""
    property_ids: List[int]
    integration_code: str


class BulkSyncResult(BaseModel):
    """一括同期結果"""
    success: int
    failed: int
    errors: List[dict]


# ========================================
# 連携先マスター
# ========================================

@router.get("/", response_model=List[Integration])
async def get_integrations():
    """連携先一覧を取得"""
    with READatabase.cursor() as (cur, conn):
        cur.execute("""
            SELECT id, code, name, description, is_active, sync_endpoint, icon_class
            FROM m_integrations
            ORDER BY display_order
        """)
        rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "code": row[1],
                "name": row[2],
                "description": row[3],
                "is_active": row[4],
                "sync_endpoint": row[5],
                "icon_class": row[6]
            }
            for row in rows
        ]


@router.patch("/{code}", response_model=Integration)
async def update_integration(code: str, data: IntegrationUpdate):
    """連携先の有効/無効を切り替え"""
    with READatabase.cursor() as (cur, conn):
        cur.execute("""
            UPDATE m_integrations
            SET is_active = %s, updated_at = NOW()
            WHERE code = %s
            RETURNING id, code, name, description, is_active, sync_endpoint, icon_class
        """, (data.is_active, code))
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"連携先 {code} が見つかりません")

        conn.commit()
        return {
            "id": row[0],
            "code": row[1],
            "name": row[2],
            "description": row[3],
            "is_active": row[4],
            "sync_endpoint": row[5],
            "icon_class": row[6]
        }


# ========================================
# 物件同期状態
# ========================================

@router.get("/sync-status")
async def get_sync_status(limit: int = 100, offset: int = 0):
    """物件の同期状態一覧を取得"""
    with READatabase.cursor() as (cur, conn):
        # アクティブな連携先を取得
        cur.execute("""
            SELECT code FROM m_integrations WHERE is_active = true ORDER BY display_order
        """)
        active_codes = [row[0] for row in cur.fetchall()]

        # 物件一覧と同期状態を取得
        cur.execute("""
            SELECT
                p.id,
                p.property_name,
                p.zoho_id,
                p.zoho_synced_at,
                p.zoho_sync_status
            FROM properties p
            ORDER BY p.updated_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))

        results = []
        for row in cur.fetchall():
            integrations = {}

            # ZOHO同期状態
            if 'zoho' in active_codes:
                integrations['zoho'] = {
                    'synced': row[2] is not None,
                    'external_id': row[2],
                    'synced_at': str(row[3]) if row[3] else None,
                    'status': row[4]
                }

            # 他の連携先は将来対応（homes_id, reins_id等をpropertiesに追加時）
            for code in active_codes:
                if code not in integrations:
                    integrations[code] = {
                        'synced': False,
                        'external_id': None,
                        'synced_at': None,
                        'status': None
                    }

            results.append({
                'property_id': row[0],
                'property_name': row[1],
                'integrations': integrations
            })

        # 総件数
        cur.execute("SELECT COUNT(*) FROM properties")
        total = cur.fetchone()[0]

        return {
            'data': results,
            'total': total,
            'limit': limit,
            'offset': offset,
            'active_integrations': active_codes
        }


@router.get("/sync-summary")
async def get_sync_summary():
    """同期状態サマリーを取得"""
    with READatabase.cursor() as (cur, conn):
        # 総物件数
        cur.execute("SELECT COUNT(*) FROM properties")
        total = cur.fetchone()[0]

        # ZOHO同期済み
        cur.execute("SELECT COUNT(*) FROM properties WHERE zoho_id IS NOT NULL")
        zoho_synced = cur.fetchone()[0]

        # アクティブな連携先
        cur.execute("""
            SELECT code, name, is_active, sync_endpoint
            FROM m_integrations
            ORDER BY display_order
        """)
        integrations = []
        for row in cur.fetchall():
            synced_count = 0
            if row[0] == 'zoho':
                synced_count = zoho_synced
            # 他の連携先は将来対応

            integrations.append({
                'code': row[0],
                'name': row[1],
                'is_active': row[2],
                'has_endpoint': row[3] is not None,
                'synced_count': synced_count,
                'unsynced_count': total - synced_count if row[2] else 0
            })

        return {
            'total_properties': total,
            'integrations': integrations
        }


# ========================================
# 一括同期
# ========================================

@router.post("/bulk-sync", response_model=BulkSyncResult)
async def bulk_sync(request: BulkSyncRequest):
    """物件を一括同期"""
    # 連携先のエンドポイントを取得
    with READatabase.cursor() as (cur, conn):
        cur.execute("""
            SELECT sync_endpoint, is_active
            FROM m_integrations
            WHERE code = %s
        """, (request.integration_code,))
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"連携先 {request.integration_code} が見つかりません")

        if not row[1]:
            raise HTTPException(status_code=400, detail=f"連携先 {request.integration_code} は無効です")

        if not row[0]:
            raise HTTPException(status_code=400, detail=f"連携先 {request.integration_code} の同期エンドポイントが設定されていません")

    # 対応する同期処理を呼び出し
    if request.integration_code == 'zoho':
        # ZOHOの場合は既存のsync APIを利用
        from app.api.api_v1.endpoints.zoho import sync_to_zoho, ZohoSyncRequest
        zoho_request = ZohoSyncRequest(property_ids=request.property_ids)
        result = await sync_to_zoho(zoho_request)
        return {
            'success': result['success'],
            'failed': result['failed'],
            'errors': result['errors']
        }
    else:
        # 他の連携先は将来対応
        raise HTTPException(
            status_code=501,
            detail=f"連携先 {request.integration_code} の同期処理は未実装です"
        )
