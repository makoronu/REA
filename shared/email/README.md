# shared/email - メール送信モジュール

## 概要

SMTP経由でメールを送信する共通モジュール。

## ファイル構成

| ファイル | 役割 |
|---------|------|
| `__init__.py` | エクスポート |
| `config.py` | SMTP設定（環境変数から読み込み） |
| `service.py` | メール送信サービス |

## 環境変数（.env）

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@example.com
SMTP_FROM_NAME=REA System
FRONTEND_URL=https://realestateautomation.net
PASSWORD_RESET_EXPIRE_HOURS=24
```

## 使い方

```python
from shared.email import EmailService

# 基本的なメール送信
EmailService.send_email(
    to_email="user@example.com",
    subject="件名",
    body_text="本文（テキスト）",
    body_html="<p>本文（HTML）</p>"  # オプション
)

# パスワードリセットメール
EmailService.send_password_reset_email(
    to_email="user@example.com",
    reset_token="xxxxx",
    user_name="ユーザー名"
)

# ウェルカムメール（新規登録）
EmailService.send_welcome_email(
    to_email="user@example.com",
    user_name="ユーザー名",
    reset_token="xxxxx"
)
```

## 注意事項

- SMTP_USER, SMTP_PASSWORDが未設定の場合、メールは送信されず、ログに出力される
- Gmail使用時はアプリパスワードを生成して使用（2段階認証必須）
