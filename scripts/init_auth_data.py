#!/usr/bin/env python3
"""
認証初期データ投入スクリプト

- m_roles: super_admin, admin, user
- organizations: shirokuma2103
- users: 開発者アカウント（パスワードはメールで設定）

Usage:
    PYTHONPATH=. python3 scripts/init_auth_data.py
"""
import sys
import os
import secrets
from datetime import datetime, timezone, timedelta

# パス設定
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import READatabase
from shared.email import EmailService, EmailConfig


def init_roles(cur, conn):
    """ロール初期データ"""
    roles = [
        ('super_admin', 'システム管理者', 100),
        ('admin', '会社管理者', 50),
        ('user', '一般ユーザー', 10),
    ]

    for code, name, level in roles:
        cur.execute('SELECT id FROM m_roles WHERE code = %s', (code,))
        if not cur.fetchone():
            cur.execute('''
                INSERT INTO m_roles (code, name, level)
                VALUES (%s, %s, %s)
            ''', (code, name, level))
            print("  Created role: {}".format(code))
        else:
            print("  Role exists: {}".format(code))

    conn.commit()


def init_organization(cur, conn):
    """組織初期データ"""
    code = 'shirokuma2103'
    name = '株式会社しろくま建物管理'

    cur.execute('SELECT id FROM organizations WHERE code = %s', (code,))
    row = cur.fetchone()
    if not row:
        cur.execute('''
            INSERT INTO organizations (code, name)
            VALUES (%s, %s)
            RETURNING id
        ''', (code, name))
        org_id = cur.fetchone()[0]
        print("  Created organization: {} (id={})".format(code, org_id))
    else:
        org_id = row[0]
        print("  Organization exists: {} (id={})".format(code, org_id))

    conn.commit()
    return org_id


def create_developer_account(cur, conn, org_id):
    """開発者アカウント作成（パスワードなし、メールでリセット）"""
    email = 'makoto_yaguchi@shirokuma2103.com'
    name = '矢口誠'

    cur.execute('SELECT id FROM users WHERE email = %s', (email,))
    if cur.fetchone():
        print("  User already exists: {}".format(email))
        return None

    # super_admin role_id取得
    cur.execute('SELECT id FROM m_roles WHERE code = %s', ('super_admin',))
    role_row = cur.fetchone()
    if not role_row:
        print("  ERROR: super_admin role not found")
        return None
    role_id = role_row[0]

    # ダミーパスワードハッシュ（ログイン不可にするため）
    dummy_hash = '$2b$12$INVALID_HASH_REQUIRE_PASSWORD_RESET_VIA_EMAIL'

    # ユーザー作成
    cur.execute('''
        INSERT INTO users (organization_id, role_id, email, password_hash, name, is_active)
        VALUES (%s, %s, %s, %s, %s, true)
        RETURNING id
    ''', (org_id, role_id, email, dummy_hash, name))
    user_id = cur.fetchone()[0]
    print("  Created user: {} (id={})".format(email, user_id))

    # パスワードリセットトークン生成
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=EmailConfig.PASSWORD_RESET_EXPIRE_HOURS)

    cur.execute('''
        INSERT INTO password_reset_tokens (user_id, email, token, expires_at)
        VALUES (%s, %s, %s, %s)
    ''', (user_id, email, token, expires_at))

    conn.commit()

    # メール送信
    print("  Sending welcome email...")
    EmailService.send_welcome_email(email, name, token)

    return user_id


def main():
    print("=== REA 認証初期データ投入 ===\n")

    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        print("[1] ロール作成")
        init_roles(cur, conn)

        print("\n[2] 組織作成")
        org_id = init_organization(cur, conn)

        print("\n[3] 開発者アカウント作成")
        create_developer_account(cur, conn, org_id)

        print("\n=== 完了 ===")
        print("\nSMTP設定がされていない場合、メールは送信されません。")
        print("その場合は手動でパスワードリセットトークンを確認してください:")
        print("  SELECT token FROM password_reset_tokens ORDER BY id DESC LIMIT 1;")

    except Exception as e:
        conn.rollback()
        print("ERROR: {}".format(str(e)))
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    main()
