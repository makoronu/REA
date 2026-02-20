# テスト依頼書: Seg 16a セキュリティ+バックエンド修正

**日付:** 2026-02-20
**変更ファイル:** 5件

---

## 変更内容

| # | 修正 | ファイル | 内容 |
|---|------|---------|------|
| P9 | admin認証追加 | admin.py | GET /property-types, GET /field-visibility に認証チェック追加 |
| P10 | 機密ログ除去 | zoho/auth.py | print()→logger（トークン値をログ出力しない） |
| P2 | httpxタイムアウト | zoho/auth.py | httpx.AsyncClient(timeout=10) |
| P1 | deleted_at漏れ | zoho.py | zoho_import_staging 3クエリにフィルタ追加 |
| P5 | naive datetime | scrapers_common.py | datetime.now()→datetime.now(timezone.utc) |

---

## テスト項目

### 1. admin認証（P9）

**正常系:**
- [ ] ログイン状態でフィールド表示設定画面（/admin/field-visibility）を開く → 正常にデータ表示
- [ ] ログイン状態で物件種別一覧が取得できる
- [ ] フィールド表示設定の変更・保存が正常動作する

**異常系:**
- [ ] 未ログイン状態でAPI直接アクセス `curl https://realestateautomation.net/api/v1/admin/property-types` → 401エラー
- [ ] 未ログイン状態で `curl https://realestateautomation.net/api/v1/admin/field-visibility` → 401エラー

---

### 2. ZOHO認証ログ（P10）

**確認:**
- [ ] ZOHOインポート画面（/import/zoho）を開く → 正常動作
- [ ] サーバーログにZOHOリフレッシュトークンの値が出力されていないことを確認

---

### 3. ZOHO staging deleted_at（P1）

**正常系:**
- [ ] ZOHOインポート → インポート状態が正常表示される
- [ ] 失敗レコード一覧が正常表示される

---

### 4. フィールド表示設定画面のfetch→api変換（P3a）

**正常系:**
- [ ] フィールド表示設定画面を開く → データが正常にロードされる
- [ ] テーブル切替（properties/building_info/land_info） → 正常にデータ切替
- [ ] 表示設定の変更 → 保存ボタンクリック → 成功メッセージ表示
- [ ] 必須設定タブに切替 → 変更 → 保存 → 成功メッセージ

**異常系:**
- [ ] 認証切れ状態 → 画面アクセス → ログインページにリダイレクト

---

## 攻撃ポイント

1. **認証バイパス**: `Authorization`ヘッダーなしでadmin GETエンドポイントを叩く → 401が返ること
2. **不正トークン**: 無効なJWTで叩く → 401が返ること

---

## テスト環境

- 本番: https://realestateautomation.net
- API: https://realestateautomation.net/api/v1/
