# REA デプロイ設定

## ConoHa VPS

| 項目 | 値 |
|------|-----|
| IP | 160.251.196.148 |
| ドメイン | realestateautomation.net |
| SSH | `ssh rea-conoha` または `ssh -i ~/.ssh/REA.pem root@160.251.196.148` |

## ConoHa API（未検証）

| 項目 | 値 |
|------|-----|
| テナントID | 642bc76289c24122bc8c1febb6d0837e |
| テナント名 | gnct15016060 |
| APIユーザー | gncu15016060 |
| APIパスワード | c6aqmZWgvybU |

## DNS設定

- Aレコード: @ → 160.251.196.148（設定済み）

## デプロイ前TODO

- [ ] ログイン機能（認証）を実装
- [ ] 管理画面のアクセス制御
- [ ] 本番環境設定
- [ ] Nginx設定
- [ ] SSL証明書（Let's Encrypt）

## Nginx設定

- 設定ファイル: `/etc/nginx/sites-available/rea`
- フロントエンド: `/opt/REA/rea-admin/dist`
- API: `proxy_pass http://127.0.0.1:8005`
- キャッシュ制御: HTML・APIはno-cache、静的アセットは長期キャッシュ

## 環境差異（ローカル vs 本番）

### パス

| 項目 | ローカル | 本番 |
|------|---------|------|
| プロジェクトルート | `~/my_programing/REA` | `/opt/REA` |
| PYTHONPATH | `~/my_programing/REA` | `/opt/REA` |
| Python実行 | `python3` | `/opt/REA/venv/bin/python3` |
| pip | `pip3` | `/opt/REA/venv/bin/pip` |
| フロントエンドビルド | `npm run dev` | `npm run build` → dist配信 |

### 環境変数（.env）

| 項目 | ローカル | 本番 |
|------|---------|------|
| DATABASE_URL | `yaguchimakoto@localhost:5432` | `rea_user:パスワード@localhost:5432` |
| JWT_SECRET_KEY | 開発用キー | 本番用キー（異なる） |
| JWT_EXPIRE_MINUTES | 480（8時間） | 60（1時間） |
| SMTP_HOST | smtp.gmail.com | localhost（Postfix） |
| SMTP_PORT | 587 | 25 |
| DEBUG | なし | false |
| ENVIRONMENT | なし | production |
| ZOHO_* | 設定あり | 設定済み（2025-12-18追加） |
| REINFOLIB_API_KEY | 設定あり | 設定済み（2025-12-18追加） |

### 本番固有設定

| ファイル | 用途 |
|---------|------|
| `/opt/REA/.env` | バックエンド環境変数 |
| `/etc/systemd/system/rea-api.service` | APIサービス管理 |
| `/etc/nginx/sites-available/rea` | Nginx設定 |
| `/etc/postfix/main.cf` | メール送信設定 |

### デプロイ手順

```bash
# 1. コード同期
ssh rea-conoha "cd /opt/REA && git pull origin main"

# 2. フロントエンドビルド
ssh rea-conoha "cd /opt/REA/rea-admin && npm install && npm run build"

# 3. API再起動
ssh rea-conoha "sudo systemctl restart rea-api"

# 4. 確認
ssh rea-conoha "sudo systemctl status rea-api"
curl -s https://realestateautomation.net/api/v1/health | jq
```

### 本番のみ必要な操作

- **Nginx再読み込み**: `sudo systemctl reload nginx`
- **ログ確認**: `sudo journalctl -u rea-api -f`
- **DBバックアップ**: `sudo -u postgres pg_dump real_estate_db > /tmp/backup.sql`

## 備考

- VPS再構築済み（2025-12-17）
- APIキャッシュ制御追加（2025-12-18）
- 環境差異ドキュメント化（2025-12-18）
