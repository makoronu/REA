"""
ZOHO CRM APIクライアント
日本リージョン (.jp) 対応

参考: https://www.zoho.com/crm/developer/docs/api/v2/

レート制限に引っかかった場合: TOO_MANY_REQUESTS エラー
"""
import os
import httpx
from typing import List, Dict, Any, Optional
from .auth import zoho_auth


class ZohoClient:
    """ZOHO CRM APIクライアント"""

    def __init__(self):
        self.auth = zoho_auth
        self.module_name = os.getenv("ZOHO_MODULE_API_NAME", "DB")

    def _get_base_url(self) -> str:
        """APIベースURLを取得（api_domainから動的に構築）"""
        api_domain = self.auth.get_api_domain()
        return f"{api_domain}/crm/v2"

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """認証付きAPIリクエスト"""
        access_token = await self.auth.get_access_token()
        base_url = self._get_base_url()

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{base_url}{endpoint}",
                headers={
                    "Authorization": f"Zoho-oauthtoken {access_token}",
                    "Content-Type": "application/json"
                },
                params=params,
                json=json_data,
                timeout=30.0
            )

            # レート制限エラーをチェック
            if response.status_code == 429:
                raise Exception("ZOHO API レート制限に達しました。しばらく待ってから再試行してください。")

            response.raise_for_status()
            return response.json()

    async def get_modules(self) -> List[Dict]:
        """利用可能なモジュール一覧を取得"""
        result = await self._request("GET", "/settings/modules")
        return result.get("modules", [])

    async def get_fields(self, module: Optional[str] = None) -> List[Dict]:
        """モジュールのフィールド一覧を取得"""
        module = module or self.module_name
        result = await self._request("GET", f"/settings/fields", params={"module": module})
        return result.get("fields", [])

    async def get_records(
        self,
        module: Optional[str] = None,
        page: int = 1,
        per_page: int = 200,
        fields: Optional[List[str]] = None,
        criteria: Optional[str] = None
    ) -> Dict[str, Any]:
        """レコード一覧を取得"""
        module = module or self.module_name
        params = {
            "page": page,
            "per_page": per_page
        }
        if fields:
            params["fields"] = ",".join(fields)
        if criteria:
            params["criteria"] = criteria

        result = await self._request("GET", f"/{module}", params=params)
        return {
            "data": result.get("data", []),
            "info": result.get("info", {})
        }

    async def get_record(self, record_id: str, module: Optional[str] = None) -> Optional[Dict]:
        """特定のレコードを取得"""
        module = module or self.module_name
        result = await self._request("GET", f"/{module}/{record_id}")
        data = result.get("data", [])
        return data[0] if data else None

    async def search_records(
        self,
        criteria: str,
        module: Optional[str] = None,
        page: int = 1,
        per_page: int = 200
    ) -> Dict[str, Any]:
        """条件でレコードを検索"""
        module = module or self.module_name
        params = {
            "criteria": criteria,
            "page": page,
            "per_page": per_page
        }
        result = await self._request("GET", f"/{module}/search", params=params)
        return {
            "data": result.get("data", []),
            "info": result.get("info", {})
        }

    async def test_connection(self) -> Dict[str, Any]:
        """接続テスト"""
        try:
            modules = await self.get_modules()
            # 物件DBモジュールが存在するか確認
            module_exists = any(m.get("api_name") == self.module_name for m in modules)
            return {
                "success": True,
                "module_exists": module_exists,
                "module_name": self.module_name,
                "total_modules": len(modules)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# シングルトンインスタンス
zoho_client = ZohoClient()
