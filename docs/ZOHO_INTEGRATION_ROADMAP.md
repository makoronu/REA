# ZOHO CRM 連携ロードマップ

## 概要

ZOHO CRM から物件データを REA システムにインポートし、同期する機能。

**同期方向**: ZOHO CRM → REA（一方向）
**認証方式**: OAuth 2.0（認証情報取得済み）

---

## フェーズ構成

```
[Phase 1: 認証基盤] → [Phase 2: データマッピング] → [Phase 3: インポート機能] → [Phase 4: 同期管理]
```

---

## Phase 1: 認証基盤（1-2日）

### 1.1 環境変数設定
```bash
# .env に追加
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REDIRECT_URI=http://localhost:8005/api/v1/zoho/callback
ZOHO_REFRESH_TOKEN=  # OAuth認証後に取得
```

### 1.2 OAuth 2.0 認証フロー実装
- [ ] `/api/v1/zoho/auth` - 認証開始エンドポイント
- [ ] `/api/v1/zoho/callback` - コールバック（アクセストークン取得）
- [ ] `/api/v1/zoho/status` - 接続状態確認
- [ ] アクセストークンの自動リフレッシュ機能

### 1.3 ファイル構成
```
rea-api/app/
├── api/api_v1/endpoints/
│   └── zoho.py              # ZOHO APIエンドポイント
├── services/
│   └── zoho/
│       ├── __init__.py
│       ├── auth.py          # OAuth認証
│       ├── client.py        # APIクライアント
│       └── mapper.py        # データマッピング
└── schemas/
    └── zoho.py              # Pydanticスキーマ
```

### 1.4 成果物
- ZOHO CRM への接続確認ボタン（フロントエンド）
- 接続状態表示（成功/失敗/未接続）

---

## Phase 2: データマッピング設計（1日）

### 2.1 ZOHO CRM モジュール調査
```
GET /crm/v2/settings/modules
```
- 物件データがどのモジュールにあるか確認
- カスタムモジュールの場合はAPI名を特定

### 2.2 フィールドマッピング定義

**マッピングテーブル作成**
```sql
CREATE TABLE zoho_field_mappings (
    id SERIAL PRIMARY KEY,
    zoho_module VARCHAR(100) NOT NULL,     -- ZOHO側モジュール名
    zoho_field VARCHAR(100) NOT NULL,      -- ZOHO側フィールドAPI名
    rea_table VARCHAR(100) NOT NULL,       -- REA側テーブル名
    rea_column VARCHAR(100) NOT NULL,      -- REA側カラム名
    transform_type VARCHAR(50),            -- 変換タイプ（direct/enum/custom）
    transform_config JSONB,                -- 変換設定
    is_required BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(zoho_module, zoho_field)
);
```

### 2.3 想定されるマッピング例

| ZOHO フィールド | REA カラム | 変換 |
|---------------|-----------|------|
| Property_Name | property_name | direct |
| Address | address | direct |
| Price | sale_price | direct |
| Property_Type | property_type | enum |
| Status | status | enum |
| Land_Area | land_area | direct |
| Building_Area | building_area | direct |
| Built_Year | construction_date | date |
| Nearest_Station | - | custom（最寄駅検索） |

### 2.4 成果物
- マッピング定義ファイル（YAML/JSON）
- マッピング編集UI（管理画面）

---

## Phase 3: インポート機能（2-3日）

### 3.1 バックエンドAPI

**ZOHO データ取得**
```python
GET /api/v1/zoho/properties
# ZOHOから物件一覧を取得（プレビュー用）

GET /api/v1/zoho/properties/{zoho_id}
# ZOHO物件詳細を取得
```

**インポート実行**
```python
POST /api/v1/zoho/import
# 選択した物件をREAにインポート
{
    "zoho_ids": ["123", "456", "789"],
    "options": {
        "update_existing": true,  # 既存物件を更新するか
        "auto_geocode": true      # 住所から緯度経度を自動取得するか
    }
}

GET /api/v1/zoho/import/{job_id}/status
# インポートジョブの進捗確認
```

### 3.2 インポート処理フロー

```
1. ZOHO API から物件データ取得
   ↓
2. フィールドマッピングに従ってデータ変換
   ↓
3. バリデーション（必須項目チェック）
   ↓
4. 重複チェック（zoho_id で既存物件確認）
   ↓
5. REA データベースに保存
   - 新規: INSERT
   - 既存: UPDATE（オプション）
   ↓
6. 自動処理（オプション）
   - ジオコーディング
   - 最寄駅検索
   - 周辺施設取得
   ↓
7. インポート結果を返却
```

### 3.3 物件テーブルへの追加カラム

```sql
-- propertiesテーブルにZOHO連携用カラム追加
ALTER TABLE properties ADD COLUMN IF NOT EXISTS zoho_id VARCHAR(100) UNIQUE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS zoho_synced_at TIMESTAMP;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS zoho_sync_status VARCHAR(20); -- synced/pending/error
```

### 3.4 フロントエンドUI

**インポートページ（/import/zoho）**
```
┌────────────────────────────────────────────────────┐
│ ZOHO CRM インポート                                 │
├────────────────────────────────────────────────────┤
│ 接続状態: ● 接続済み         [再接続]              │
├────────────────────────────────────────────────────┤
│                                                    │
│ ┌──────────────────────────────────────────────┐ │
│ │ □ 物件A - 東京都渋谷区...    ¥50,000,000    │ │
│ │ □ 物件B - 東京都新宿区...    ¥35,000,000    │ │
│ │ ☑ 物件C - 東京都港区...      ¥80,000,000    │ │
│ │ □ 物件D - 神奈川県横浜市...  ¥25,000,000    │ │
│ └──────────────────────────────────────────────┘ │
│                                                    │
│ オプション:                                        │
│ ☑ 既存物件を更新する                              │
│ ☑ 住所から位置情報を自動取得                       │
│                                                    │
│ [全選択] [選択解除]           [インポート実行]     │
│                                                    │
├────────────────────────────────────────────────────┤
│ 最終インポート: 2025-12-14 15:30 (5件成功)         │
└────────────────────────────────────────────────────┘
```

### 3.5 成果物
- ZOHO物件一覧表示画面
- インポート実行ボタン
- インポート結果表示（成功/失敗/スキップ件数）

---

## Phase 4: 同期管理（1-2日）

### 4.1 同期履歴テーブル

```sql
CREATE TABLE zoho_sync_logs (
    id SERIAL PRIMARY KEY,
    zoho_id VARCHAR(100) NOT NULL,
    property_id INTEGER REFERENCES properties(id),
    action VARCHAR(20) NOT NULL,  -- import/update/skip/error
    status VARCHAR(20) NOT NULL,  -- success/failed
    error_message TEXT,
    request_data JSONB,
    response_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_zoho_sync_logs_zoho_id ON zoho_sync_logs(zoho_id);
CREATE INDEX idx_zoho_sync_logs_created_at ON zoho_sync_logs(created_at);
```

### 4.2 同期状態管理

**物件一覧での同期状態表示**
- 🟢 同期済み（最新）
- 🟡 更新あり（ZOHO側で変更あり）
- 🔴 エラー
- ⚪ 未連携

### 4.3 差分検出（オプション）

```python
GET /api/v1/zoho/diff
# ZOHOとREAの差分を検出
# - ZOHO側で更新された物件
# - REAにない新規物件
# - ZOHOから削除された物件
```

### 4.4 成果物
- 同期履歴一覧画面
- 物件一覧での同期状態表示
- 差分レポート機能

---

## API エンドポイント一覧

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | /api/v1/zoho/auth | OAuth認証開始 |
| GET | /api/v1/zoho/callback | OAuthコールバック |
| GET | /api/v1/zoho/status | 接続状態確認 |
| GET | /api/v1/zoho/properties | ZOHO物件一覧取得 |
| GET | /api/v1/zoho/properties/{id} | ZOHO物件詳細取得 |
| POST | /api/v1/zoho/import | インポート実行 |
| GET | /api/v1/zoho/import/{job_id}/status | インポート状態確認 |
| GET | /api/v1/zoho/sync-logs | 同期履歴一覧 |
| GET | /api/v1/zoho/diff | 差分検出 |
| GET | /api/v1/zoho/mappings | マッピング一覧 |
| PUT | /api/v1/zoho/mappings | マッピング更新 |

---

## 実装順序

### Day 1: 認証基盤
1. [ ] 環境変数設定
2. [ ] OAuth 2.0 認証フロー実装
3. [ ] 接続確認UI

### Day 2: データマッピング
4. [ ] ZOHO CRMモジュール/フィールド調査
5. [ ] マッピングテーブル作成
6. [ ] マッピング定義

### Day 3-4: インポート機能
7. [ ] ZOHO物件取得API
8. [ ] データ変換処理
9. [ ] インポートAPI
10. [ ] インポートUI

### Day 5: 同期管理
11. [ ] 同期履歴テーブル
12. [ ] 同期状態表示
13. [ ] 差分検出（オプション）

### Day 6: テスト・調整
14. [ ] E2Eテスト
15. [ ] エラーハンドリング強化
16. [ ] ドキュメント整備

---

## 注意事項

### ZOHO API 制限
- レート制限: 1分あたり100リクエスト（無料プラン）
- 1日あたり5,000リクエスト（無料プラン）
- ページネーション: 最大200件/リクエスト

### セキュリティ
- アクセストークンは暗号化して保存
- リフレッシュトークンは.envで管理（Gitにコミットしない）
- APIキーのローテーション対応

### エラーハンドリング
- ZOHO API エラー時のリトライ（指数バックオフ）
- 部分失敗時のロールバック or 継続選択
- エラーログの詳細記録

---

## 将来の拡張

### 双方向同期（検討中）
- REA → ZOHO の更新同期
- 競合解決ルールの定義
- リアルタイム同期（Webhook）

### 他システム連携
- この実装をベースに、他CRM（Salesforce等）連携にも対応可能
- 共通インターフェース設計

---

## 参考リンク

- [ZOHO CRM API ドキュメント](https://www.zoho.com/crm/developer/docs/api/v2/)
- [OAuth 2.0 認証](https://www.zoho.com/crm/developer/docs/api/v2/oauth-overview.html)
- [APIレート制限](https://www.zoho.com/crm/developer/docs/api/v2/api-limits.html)
