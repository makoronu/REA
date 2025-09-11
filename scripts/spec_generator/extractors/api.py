"""
API情報抽出モジュール
"""
import sys
from pathlib import Path

import requests

sys.path.append(str(Path(__file__).parent.parent))
from config import Config


class APIExtractor:
    def __init__(self):
        self.config = Config()

    def extract(self):
        """API情報を抽出"""
        try:
            return self._extract_live_api()
        except Exception as e:
            print(f"⚠️ API接続失敗: {e}")
            return self._load_static_api()

    def _extract_live_api(self):
        """稼働中のAPIから情報を抽出"""
        # OpenAPI仕様を取得
        resp = requests.get(
            f"{self.config.API_URL}/openapi.json", timeout=self.config.API_TIMEOUT
        )
        openapi = resp.json()

        # エンドポイント抽出
        endpoints = []
        for path, methods in openapi.get("paths", {}).items():
            for method, spec in methods.items():
                endpoints.append(
                    {
                        "method": method.upper(),
                        "path": path,
                        "summary": spec.get("summary", ""),
                        "tags": spec.get("tags", []),
                    }
                )

        return {
            "total_endpoints": len(endpoints),
            "endpoints": endpoints,
            "base_url": self.config.API_URL,
            "title": openapi.get("info", {}).get("title", "REA API"),
            "version": openapi.get("info", {}).get("version", "1.0.0"),
        }

    def _load_static_api(self):
        """静的データを返す（フォールバック）"""
        return {
            "total_endpoints": 8,
            "endpoints": [
                {
                    "method": "GET",
                    "path": "/api/v1/properties/",
                    "summary": "物件一覧取得",
                    "tags": ["properties"],
                },
                {
                    "method": "POST",
                    "path": "/api/v1/properties/",
                    "summary": "物件作成",
                    "tags": ["properties"],
                },
                {
                    "method": "GET",
                    "path": "/api/v1/properties/{property_id}",
                    "summary": "物件詳細取得",
                    "tags": ["properties"],
                },
                {
                    "method": "PUT",
                    "path": "/api/v1/properties/{property_id}",
                    "summary": "物件更新",
                    "tags": ["properties"],
                },
                {
                    "method": "DELETE",
                    "path": "/api/v1/properties/{property_id}",
                    "summary": "物件削除",
                    "tags": ["properties"],
                },
                {
                    "method": "GET",
                    "path": "/api/v1/properties/by-contractor/{company_name}",
                    "summary": "元請会社別物件取得",
                    "tags": ["properties"],
                },
                {
                    "method": "GET",
                    "path": "/api/v1/properties/contractors/contacts",
                    "summary": "元請会社連絡先一覧",
                    "tags": ["properties"],
                },
                {
                    "method": "GET",
                    "path": "/health",
                    "summary": "ヘルスチェック",
                    "tags": ["system"],
                },
            ],
            "base_url": self.config.API_URL,
            "title": "REA API",
            "version": "1.0.0",
        }
