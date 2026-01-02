"""
ZOHO CRM OAuth 2.0 認証
日本リージョン (.jp) 対応

参考: https://www.zoho.com/crm/developer/docs/api/v2/access-refresh.html

API上限（24時間ローリングウィンドウ）:
- Free: 5,000クレジット
- Standard: 50,000 + (ユーザー×250)、最大10万
- Professional: 50,000 + (ユーザー×500)、最大300万
- Enterprise: 50,000 + (ユーザー×1,000)、最大500万

エラー時: TOO_MANY_REQUESTS
"""
import os
import httpx
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path

# .envファイルを明示的に読み込む
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parents[5] / ".env"  # REA/.env
load_dotenv(env_path)

from app.core.config import settings


class ZohoAuth:
    """ZOHO OAuth 2.0 認証クラス"""

    # 日本リージョンのエンドポイント（設定ファイルから取得）
    AUTH_URL = settings.ZOHO_AUTH_URL
    TOKEN_URL = settings.ZOHO_TOKEN_URL

    def __init__(self):
        self.client_id = os.getenv("ZOHO_CLIENT_ID")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        self.redirect_uri = os.getenv("ZOHO_REDIRECT_URI", "http://localhost:8005/api/v1/zoho/callback")
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")

        # アクセストークンのキャッシュ
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        # APIドメイン（トークンレスポンスから取得）
        self._api_domain: Optional[str] = None

    def get_auth_url(self, scope: str = "ZohoCRM.modules.ALL,ZohoCRM.settings.ALL") -> str:
        """OAuth認証URLを生成"""
        params = {
            "scope": scope,
            "client_id": self.client_id,
            "response_type": "code",
            "access_type": "offline",
            "redirect_uri": self.redirect_uri,
            "prompt": "consent"
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query}"

    async def exchange_code_for_tokens(self, code: str) -> dict:
        """認証コードをアクセストークンとリフレッシュトークンに交換"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "code": code
                }
            )
            response.raise_for_status()
            data = response.json()

            # リフレッシュトークンを取得したら保存（手動で.envに設定が必要）
            if "refresh_token" in data:
                self.refresh_token = data["refresh_token"]
                print(f"[ZOHO] リフレッシュトークン取得: {data['refresh_token']}")
                print("[ZOHO] このトークンを .env の ZOHO_REFRESH_TOKEN に設定してください")

            # APIドメインを保存（これを使ってAPI呼び出しを行う）
            if "api_domain" in data:
                self._api_domain = data["api_domain"]
                print(f"[ZOHO] APIドメイン: {self._api_domain}")

            # アクセストークンをキャッシュ
            self._access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            return data

    async def get_access_token(self) -> str:
        """有効なアクセストークンを取得（必要に応じてリフレッシュ）"""
        # キャッシュが有効ならそれを返す
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                return self._access_token

        # リフレッシュトークンでアクセストークンを取得
        if not self.refresh_token:
            raise ValueError("リフレッシュトークンが設定されていません。先にOAuth認証を完了してください。")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token
                }
            )
            response.raise_for_status()
            data = response.json()

            self._access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            # APIドメインを更新
            if "api_domain" in data:
                self._api_domain = data["api_domain"]

            return self._access_token

    def get_api_domain(self) -> str:
        """APIドメインを取得（デフォルトは日本リージョン）"""
        return self._api_domain or settings.ZOHO_API_DOMAIN

    def is_configured(self) -> bool:
        """認証情報が設定されているかチェック"""
        return bool(self.client_id and self.client_secret)

    def has_refresh_token(self) -> bool:
        """リフレッシュトークンが設定されているかチェック"""
        return bool(self.refresh_token)


# シングルトンインスタンス
zoho_auth = ZohoAuth()
