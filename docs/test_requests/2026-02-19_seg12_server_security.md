# テスト依頼書: Seg 12 - サーバーセキュリティ強化

**日付:** 2026-02-19
**対象コミット:** (未コミット)

---

## テスト対象

| 対象 | 変更内容 |
|------|----------|
| /etc/systemd/system/rea-api.service | --host 0.0.0.0 → 127.0.0.1 |
| /opt/REA/.env | 権限 644 → 600 |
| /etc/nginx/sites-enabled/rea | セキュリティヘッダー5種追加 |
| /etc/nginx/nginx.conf | server_tokens off 有効化 |
| deploy.yml:59 | .env復元後 chmod 600 追加 |
| main.py:26-28 | CORS localhost 2件削除 |
| config.py | SECRET_KEY, BACKEND_CORS_ORIGINS 未使用コード削除 |

---

## 変更概要

本番サーバーのセキュリティ強化。uvicornのバインドアドレスをローカルホスト限定に変更。.envファイル権限を制限。nginxにセキュリティヘッダーを追加しバージョン情報を非表示化。デプロイスクリプトで.env権限を永続化。本番CORSからlocalhost削除。未使用の設定コード削除。

---

## テストケース

### 正常系

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | フロントエンド表示 | https://realestateautomation.net/ にアクセス | 正常に表示される |
| 2 | API認証 | ログイン → 物件一覧表示 | 正常に動作する |
| 3 | 物件編集 | 既存物件を編集→保存 | 正常に保存される |
| 4 | セキュリティヘッダー確認 | ブラウザDevTools → Network → レスポンスヘッダー | X-Frame-Options, X-Content-Type-Options, HSTS, X-XSS-Protection, Referrer-Policy が表示 |
| 5 | バージョン非表示 | レスポンスヘッダーのServer | 「nginx」のみ（バージョン番号なし） |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 6 | ポート直接アクセス | 外部からhttp://サーバーIP:8005/ にアクセス不可（UFW + 127.0.0.1バインド） |
| 7 | CORS | localhostからのリクエストが拒否されること |
| 8 | レグレッション | 全CRUD操作が正常動作すること |

---

## テスト環境

- 本番: https://realestateautomation.net/
