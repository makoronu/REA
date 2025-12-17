# 認証API
import sys
sys.path.insert(0, '/Users/yaguchimakoto/my_programing/REA')

import secrets
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timezone, timedelta

from shared.database import READatabase
from shared.auth.password import verify_password, hash_password
from shared.auth.jwt_handler import create_token, verify_token
from shared.auth.middleware import get_current_user
from shared.email import EmailService, EmailConfig

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


# ========================================
# パスワードリセット関連
# ========================================

class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class PasswordResetResponse(BaseModel):
    message: str


@router.post("/password-reset/request", response_model=PasswordResetResponse)
async def request_password_reset(request: PasswordResetRequest):
    """パスワードリセットをリクエスト（メール送信）"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # ユーザー検索
        cur.execute('''
            SELECT id, email, name FROM users WHERE email = %s AND is_active = true
        ''', (request.email,))
        row = cur.fetchone()

        # ユーザーが存在しなくても同じメッセージを返す（セキュリティ）
        if not row:
            return {"message": "メールアドレスが登録されている場合、パスワードリセット用のメールを送信しました"}

        user_id = row[0]
        email = row[1]
        name = row[2]

        # トークン生成
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=EmailConfig.PASSWORD_RESET_EXPIRE_HOURS)

        # 既存の未使用トークンを無効化
        cur.execute('''
            UPDATE password_reset_tokens
            SET used_at = NOW()
            WHERE email = %s AND used_at IS NULL
        ''', (email,))

        # 新しいトークンを保存
        cur.execute('''
            INSERT INTO password_reset_tokens (user_id, email, token, expires_at)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, email, token, expires_at))
        conn.commit()

        # メール送信
        EmailService.send_password_reset_email(email, token, name)

        return {"message": "メールアドレスが登録されている場合、パスワードリセット用のメールを送信しました"}

    finally:
        cur.close()
        conn.close()


@router.post("/password-reset/confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(request: PasswordResetConfirm):
    """パスワードリセットを実行"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # トークン検証
        cur.execute('''
            SELECT id, user_id, email, expires_at, used_at
            FROM password_reset_tokens
            WHERE token = %s
        ''', (request.token,))
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=400, detail="無効なトークンです")

        token_id = row[0]
        user_id = row[1]
        expires_at = row[3]
        used_at = row[4]

        if used_at:
            raise HTTPException(status_code=400, detail="このトークンは既に使用されています")

        if datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc):
            raise HTTPException(status_code=400, detail="トークンの有効期限が切れています")

        # パスワード更新
        new_hash = hash_password(request.new_password)
        cur.execute('''
            UPDATE users SET password_hash = %s, updated_at = NOW() WHERE id = %s
        ''', (new_hash, user_id))

        # トークンを使用済みに
        cur.execute('''
            UPDATE password_reset_tokens SET used_at = NOW() WHERE id = %s
        ''', (token_id,))

        conn.commit()

        return {"message": "パスワードを更新しました"}

    finally:
        cur.close()
        conn.close()


@router.get("/password-reset/verify/{token}")
async def verify_reset_token(token: str):
    """トークンの有効性を確認"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute('''
            SELECT expires_at, used_at
            FROM password_reset_tokens
            WHERE token = %s
        ''', (token,))
        row = cur.fetchone()

        if not row:
            return {"valid": False, "message": "無効なトークンです"}

        expires_at = row[0]
        used_at = row[1]

        if used_at:
            return {"valid": False, "message": "このトークンは既に使用されています"}

        if datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc):
            return {"valid": False, "message": "トークンの有効期限が切れています"}

        return {"valid": True, "message": "有効なトークンです"}

    finally:
        cur.close()
        conn.close()
