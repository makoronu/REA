# ユーザー管理API（会社管理者用）
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import secrets
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import dependencies
from shared.auth.middleware import get_current_user
from shared.auth.password import hash_password
from shared.auth.constants import ADMIN_ROLES
from shared.email import EmailService, EmailConfig

router = APIRouter()


# ========================================
# リクエスト/レスポンスモデル
# ========================================

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    role_id: int


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role_id: int
    role_name: str
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int


# ========================================
# ヘルパー関数
# ========================================

def require_admin(request: Request):
    """管理者権限を要求（role_codeベースで判定）"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="認証が必要です")
    # ロールコードで判定（ADMIN_ROLESはshared/auth/constants.pyで定義）
    if user.get('role_code') not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="管理者権限が必要です")
    return user


# ========================================
# エンドポイント
# ========================================

@router.get("", response_model=UserListResponse)
def list_users(
    request: Request,
    db: Session = Depends(dependencies.get_db)
):
    """自社ユーザー一覧を取得"""
    user = require_admin(request)
    org_id = user['organization_id']

    query = text("""
        SELECT
            u.id, u.email, u.name, u.role_id, r.name as role_name,
            u.is_active, u.last_login_at, u.created_at
        FROM users u
        JOIN m_roles r ON u.role_id = r.id
        WHERE u.organization_id = :org_id
        ORDER BY u.created_at DESC
    """)
    result = db.execute(query, {"org_id": org_id})

    users = []
    for row in result:
        users.append(UserResponse(
            id=row.id,
            email=row.email,
            name=row.name,
            role_id=row.role_id,
            role_name=row.role_name,
            is_active=row.is_active,
            last_login_at=row.last_login_at,
            created_at=row.created_at
        ))

    return UserListResponse(users=users, total=len(users))


@router.post("", response_model=UserResponse)
def create_user(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(dependencies.get_db)
):
    """ユーザーを作成（ウェルカムメール送信）"""
    admin = require_admin(request)
    org_id = admin['organization_id']

    # メールアドレス重複チェック
    check_query = text("SELECT id FROM users WHERE email = :email")
    existing = db.execute(check_query, {"email": user_data.email}).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています")

    # 仮パスワード生成（ユーザーはメールで再設定）
    temp_password = secrets.token_urlsafe(16)
    password_hash = hash_password(temp_password)

    # ユーザー作成
    insert_query = text("""
        INSERT INTO users (organization_id, role_id, email, password_hash, name, is_active, last_login_at, created_at, updated_at)
        VALUES (:org_id, :role_id, :email, :password_hash, :name, true, NOW(), NOW(), NOW())
        RETURNING id, created_at
    """)
    result = db.execute(insert_query, {
        "org_id": org_id,
        "role_id": user_data.role_id,
        "email": user_data.email,
        "password_hash": password_hash,
        "name": user_data.name
    })
    row = result.fetchone()
    user_id = row.id
    created_at = row.created_at

    # パスワード設定用トークン生成
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=EmailConfig.PASSWORD_RESET_EXPIRE_HOURS)

    token_query = text("""
        INSERT INTO password_reset_tokens (user_id, email, token, expires_at)
        VALUES (:user_id, :email, :token, :expires_at)
    """)
    db.execute(token_query, {
        "user_id": user_id,
        "email": user_data.email,
        "token": token,
        "expires_at": expires_at
    })

    db.commit()

    # ウェルカムメール送信
    EmailService.send_welcome_email(user_data.email, user_data.name, token)

    # ロール名取得
    role_query = text("SELECT name FROM m_roles WHERE id = :role_id")
    role_row = db.execute(role_query, {"role_id": user_data.role_id}).fetchone()
    role_name = role_row.name if role_row else "不明"

    return UserResponse(
        id=user_id,
        email=user_data.email,
        name=user_data.name,
        role_id=user_data.role_id,
        role_name=role_name,
        is_active=True,
        last_login_at=None,
        created_at=created_at
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    request: Request,
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(dependencies.get_db)
):
    """ユーザー情報を更新"""
    admin = require_admin(request)
    org_id = admin['organization_id']

    # 自社ユーザーか確認
    check_query = text("""
        SELECT u.id, u.email, u.name, u.role_id, r.name as role_name,
               u.is_active, u.last_login_at, u.created_at
        FROM users u
        JOIN m_roles r ON u.role_id = r.id
        WHERE u.id = :user_id AND u.organization_id = :org_id
    """)
    row = db.execute(check_query, {"user_id": user_id, "org_id": org_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    # 更新
    updates = []
    params = {"user_id": user_id}

    if user_data.name is not None:
        updates.append("name = :name")
        params["name"] = user_data.name
    if user_data.role_id is not None:
        updates.append("role_id = :role_id")
        params["role_id"] = user_data.role_id
    if user_data.is_active is not None:
        updates.append("is_active = :is_active")
        params["is_active"] = user_data.is_active

    if updates:
        updates.append("updated_at = NOW()")
        update_query = text(f"UPDATE users SET {', '.join(updates)} WHERE id = :user_id")
        db.execute(update_query, params)
        db.commit()

    # 更新後のデータ取得
    result = db.execute(check_query, {"user_id": user_id, "org_id": org_id}).fetchone()

    return UserResponse(
        id=result.id,
        email=result.email,
        name=result.name,
        role_id=result.role_id,
        role_name=result.role_name,
        is_active=result.is_active,
        last_login_at=result.last_login_at,
        created_at=result.created_at
    )


@router.delete("/{user_id}")
def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(dependencies.get_db)
):
    """ユーザーを無効化（削除ではなく無効化）"""
    admin = require_admin(request)
    org_id = admin['organization_id']

    # 自分自身は削除不可
    if admin['user_id'] == user_id:
        raise HTTPException(status_code=400, detail="自分自身は削除できません")

    # 自社ユーザーか確認
    check_query = text("SELECT id FROM users WHERE id = :user_id AND organization_id = :org_id")
    row = db.execute(check_query, {"user_id": user_id, "org_id": org_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    # 無効化
    update_query = text("UPDATE users SET is_active = false, updated_at = NOW() WHERE id = :user_id")
    db.execute(update_query, {"user_id": user_id})
    db.commit()

    return {"success": True, "message": "ユーザーを無効化しました"}


@router.get("/roles")
def get_roles(
    request: Request,
    db: Session = Depends(dependencies.get_db)
):
    """選択可能なロール一覧を取得"""
    admin = require_admin(request)
    admin_level = admin.get('role_level', 0)

    # 自分より低いレベルのロールのみ選択可能
    query = text("""
        SELECT id, code, name, level
        FROM m_roles
        WHERE level < :admin_level
        ORDER BY level DESC
    """)
    result = db.execute(query, {"admin_level": admin_level})

    return [
        {"id": row.id, "code": row.code, "name": row.name, "level": row.level}
        for row in result
    ]
