# テスト依頼書: システム設定管理画面

## 概要
- 日付: 2026-01-19
- 作業者: Claude
- 目的: 管理画面からGoogle Maps APIキーを設定可能にする

## 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| scripts/migrations/2026-01-19_system_settings.sql | system_settingsテーブル作成 |
| rea-api/app/api/api_v1/endpoints/settings.py | 設定CRUD API |
| rea-api/app/api/api_v1/api.py | ルーター追加 |
| rea-api/app/api/api_v1/endpoints/geo.py | DB設定優先読み込み |
| rea-admin/src/pages/Settings/SystemSettingsPage.tsx | 設定UI |
| rea-admin/src/App.tsx | ルート追加 |
| rea-admin/src/constants/apiPaths.ts | APIパス追加 |

---

## テスト項目

### 1. DBマイグレーション

#### 前提条件
- PostgreSQLにアクセス可能

#### テスト手順
1. マイグレーションSQL実行
2. system_settingsテーブル確認

#### 確認コマンド
```sql
SELECT * FROM system_settings;
```

#### 期待結果
- [ ] テーブルが作成される
- [ ] GOOGLE_MAPS_API_KEYレコードが存在（valueはNULL）

---

### 2. 設定画面アクセス

#### 前提条件
- 管理者ユーザーでログイン

#### テスト手順
1. `/settings/system` にアクセス

#### 期待結果
- [ ] システム設定画面が表示される
- [ ] GOOGLE_MAPS_API_KEY が「未設定」で表示される

---

### 3. APIキー設定

#### テスト手順
1. 「値を設定」ボタンをクリック
2. APIキーを入力（例: `AIzaSy...`）
3. 「保存」ボタンをクリック

#### 期待結果
- [ ] 保存成功メッセージが表示される
- [ ] 「設定済み」に変わる
- [ ] 値がマスク表示される（例: `AIza****************`）

---

### 4. ジオコーディング動作確認

#### 前提条件
- 有効なGoogle Maps APIキーが設定済み

#### テスト手順
1. 物件編集画面を開く
2. 住所を入力（例: 「北海道札幌市中央区北1条西2丁目」）
3. 「住所から座標を取得」ボタンをクリック

#### 期待結果
- [ ] 座標が取得される
- [ ] レスポンスのsourceが「google」

#### 確認コマンド
```bash
curl "http://localhost:8005/api/v1/geo/geocode?address=東京都渋谷区渋谷1-1-1"
```

---

### 5. 権限チェック

#### テスト手順
1. 一般ユーザーでログイン
2. `/settings/system` にアクセス

#### 期待結果
- [ ] アクセス拒否またはリダイレクト

---

## 異常系テスト

| ケース | 期待動作 |
|-------|---------|
| 空値で保存 | エラーメッセージ表示 |
| 無効なAPIキー設定後のジオコーディング | GSI/Nominatimにフォールバック |
| DB接続エラー時 | 環境変数にフォールバック |

---

## ロールバック手順

### DB
```sql
DROP TABLE IF EXISTS system_settings;
```

### コード
```bash
git revert HEAD
```

---

## 環境設定

### 起動コマンド
```bash
# API
cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005

# フロント
cd ~/my_programing/REA/rea-admin && npm run dev
```

### 管理画面URL
- ローカル: http://localhost:5173/settings/system
- 本番: https://realestateautomation.net/settings/system
