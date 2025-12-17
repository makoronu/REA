# 認証・認可モジュール

## 概要

マルチテナント対応の認証・認可システム。
dev-protocol準拠：アプリケーション層でロジック完結、DB側にトリガー/RLS不使用。

## ディレクトリ構成

```
shared/auth/
├── README.md          # このファイル
├── __init__.py
├── config.py          # 認証設定（.envから読み込み）
├── password.py        # パスワードハッシュ・検証
├── jwt_handler.py     # JWT発行・検証
├── middleware.py      # FastAPI認証ミドルウェア
└── tenant_filter.py   # テナント分離フィルタ
```

## 権限レベル

| role_code | name | level | 説明 |
|-----------|------|-------|------|
| super_admin | 開発者 | 100 | 全テナントアクセス可 |
| admin | 管理者 | 50 | 自組織のユーザー管理可 |
| user | 一般 | 10 | 自組織のデータ閲覧・編集 |

## 組織（テナント）

| id | code | 説明 |
|----|------|------|
| 1 | system | システム管理（super_admin所属用） |
| 2 | shirokuma | しろくま不動産 |
| 3~ | - | 今後追加される顧客 |

## 使い方

### 認証ミドルウェア

```python
from shared.auth.middleware import require_auth, require_admin

@app.get("/api/v1/properties")
@require_auth()  # ログイン必須
async def get_properties(request: Request):
    user = request.state.current_user
    ...

@app.post("/api/v1/org/users")
@require_admin()  # admin以上
async def create_user(request: Request):
    ...
```

### テナントフィルタ

```python
from shared.auth.tenant_filter import TenantFilter

# SELECT時
condition, params = TenantFilter.get_condition(current_user)
query = f"SELECT * FROM properties WHERE {condition}"
cursor.execute(query, params)

# INSERT時
org_id = TenantFilter.get_org_id_for_insert(current_user)
```

### パスワード

```python
from shared.auth.password import hash_password, verify_password

hashed = hash_password("plain_password")
is_valid = verify_password("plain_password", hashed)
```

### JWT

```python
from shared.auth.jwt_handler import create_token, verify_token

token = create_token({"user_id": 1, "organization_id": 2, "role_code": "admin"})
payload = verify_token(token)
```

## 環境変数（.env）

```env
JWT_SECRET_KEY=ランダム文字列（必須）
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
PASSWORD_HASH_ROUNDS=12
```

## 禁止事項（dev-protocol準拠）

- PostgreSQL RLS不使用（アプリ層で制御）
- トリガー/ストアドプロシージャ不使用
- ENUM型不使用（m_rolesマスターテーブル）
- NULL許容最小化
- SQLインジェクション対策必須（パラメータ化クエリ）
