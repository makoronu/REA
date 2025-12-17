# 認証API
import sys
sys.path.insert(0, '/Users/yaguchimakoto/my_programing/REA')

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timezone

from shared.database import READatabase
from shared.auth.password import verify_password
from shared.auth.jwt_handler import create_token, verify_token
from shared.auth.middleware import get_current_user

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    organization_id: int
    organization_name: str
    role_code: str
    role_name: str
    role_level: int


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """ログイン"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # ユーザー検索
        cur.execute('''
            SELECT
                u.id,
                u.email,
                u.name,
                u.password_hash,
                u.organization_id,
                o.name as organization_name,
                o.code as organization_code,
                r.id as role_id,
                r.code as role_code,
                r.name as role_name,
                r.level as role_level,
                u.is_active
            FROM users u
            JOIN organizations o ON u.organization_id = o.id
            JOIN m_roles r ON u.role_id = r.id
            WHERE u.email = %s
        ''', (request.email,))

        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません")

        user_data = {
            'id': row[0],
            'email': row[1],
            'name': row[2],
            'password_hash': row[3],
            'organization_id': row[4],
            'organization_name': row[5],
            'organization_code': row[6],
            'role_id': row[7],
            'role_code': row[8],
            'role_name': row[9],
            'role_level': row[10],
            'is_active': row[11],
        }

        # アカウント有効チェック
        if not user_data['is_active']:
            raise HTTPException(status_code=401, detail="アカウントが無効です")

        # パスワード検証
        if not verify_password(request.password, user_data['password_hash']):
            raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません")

        # 最終ログイン日時更新
        cur.execute('''
            UPDATE users SET last_login_at = %s WHERE id = %s
        ''', (datetime.now(timezone.utc), user_data['id']))
        conn.commit()

        # JWT発行
        token_payload = {
            'user_id': user_data['id'],
            'email': user_data['email'],
            'name': user_data['name'],
            'organization_id': user_data['organization_id'],
            'organization_code': user_data['organization_code'],
            'role_code': user_data['role_code'],
            'role_level': user_data['role_level'],
        }
        token = create_token(token_payload)

        return {
            'token': token,
            'user': {
                'id': user_data['id'],
                'email': user_data['email'],
                'name': user_data['name'],
                'organization_id': user_data['organization_id'],
                'organization_name': user_data['organization_name'],
                'role_code': user_data['role_code'],
                'role_name': user_data['role_name'],
                'role_level': user_data['role_level'],
            }
        }

    finally:
        cur.close()
        conn.close()


@router.post("/logout")
async def logout():
    """ログアウト（JWTはステートレスなのでクライアント側でトークン破棄）"""
    return {"message": "ログアウトしました"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(request: Request):
    """現在のユーザー情報を取得"""
    user = get_current_user(request)

    if not user:
        raise HTTPException(status_code=401, detail="認証が必要です")

    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute('''
            SELECT
                u.id,
                u.email,
                u.name,
                u.organization_id,
                o.name as organization_name,
                r.code as role_code,
                r.name as role_name,
                r.level as role_level
            FROM users u
            JOIN organizations o ON u.organization_id = o.id
            JOIN m_roles r ON u.role_id = r.id
            WHERE u.id = %s
        ''', (user['user_id'],))

        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

        return {
            'id': row[0],
            'email': row[1],
            'name': row[2],
            'organization_id': row[3],
            'organization_name': row[4],
            'role_code': row[5],
            'role_name': row[6],
            'role_level': row[7],
        }

    finally:
        cur.close()
        conn.close()
