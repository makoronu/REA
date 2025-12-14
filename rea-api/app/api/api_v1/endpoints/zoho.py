"""
ZOHO CRM 連携エンドポイント

機能:
- OAuth認証（認証URL生成、コールバック）
- 接続状態確認
- 物件データ取得
- インポート機能
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from typing import Optional, List
from pydantic import BaseModel

from app.services.zoho import ZohoClient, ZohoAuth
from app.services.zoho.auth import zoho_auth
from app.services.zoho.client import zoho_client


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
# OAuth認証
# ========================================

@router.get("/auth", response_model=ZohoAuthUrl)
async def get_auth_url():
    """OAuth認証URLを取得"""
    if not zoho_auth.is_configured():
        raise HTTPException(
            status_code=400,
            detail="ZOHO認証情報が設定されていません。.envにZOHO_CLIENT_IDとZOHO_CLIENT_SECRETを設定してください。"
        )

    auth_url = zoho_auth.get_auth_url()
    return {"auth_url": auth_url}


@router.get("/callback")
async def oauth_callback(code: str = Query(...)):
    """OAuthコールバック - 認証コードをトークンに交換"""
    try:
        result = await zoho_auth.exchange_code_for_tokens(code)

        # リフレッシュトークンが取得できたことを通知
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
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=message)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"トークン取得に失敗しました: {str(e)}")


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

    # 接続テスト
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fields")
async def get_fields(module: Optional[str] = None):
    """モジュールのフィールド一覧を取得"""
    try:
        fields = await zoho_client.get_fields(module)
        return {"fields": fields, "count": len(fields)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            per_page=min(per_page, 200),  # ZOHO APIの上限は200
            criteria=criteria
        )
        return {
            "data": result.get("data", []),
            "info": result.get("info", {}),
            "page": page,
            "per_page": per_page
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/properties/{zoho_id}")
async def get_zoho_property(zoho_id: str):
    """ZOHO CRMから特定の物件を取得"""
    try:
        record = await zoho_client.get_record(zoho_id)
        if not record:
            raise HTTPException(status_code=404, detail="物件が見つかりません")
        return {"data": record}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# インポート機能
# ========================================

@router.post("/import", response_model=ZohoImportResult)
async def import_properties(request: ZohoImportRequest):
    """ZOHO CRMから物件をインポート"""
    # TODO: 実装
    # 1. zoho_idsの物件を取得
    # 2. データマッピングで変換
    # 3. REAのDBに保存
    # 4. 結果を返す

    return {
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "errors": [{"message": "インポート機能は未実装です"}]
    }
