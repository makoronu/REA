# テーブル作成（DDL）

## やること
1. market_intel_db を作成（ローカル開発用）
2. DDLスクリプトを `scripts/create_tables.sql` に記述
3. 実行して確認

## 必須テーブル

### メタデータ系（REA踏襲）
- `master_categories` — カテゴリ管理（REAと同一構造）
- `master_options` — 選択肢管理（REAと同一構造、api_aliases含む）
- `column_labels` — カラム定義（REAと同一構造）

### スクレイピング固有
- `scraped_properties` — 収集物件（REA互換カラム + スクレイピング固有カラム）
- `price_history` — 価格履歴（物件ID + 価格 + 記録日時 + 前回比）
- `listing_status_history` — 掲載状態履歴（active/disappeared/reappeared）
- `scrape_sessions` — 巡回セッション（サイト + 開始/終了 + 統計）
- `scrape_sources` — 巡回対象定義（サイト + 地域 + 物件種別 + URL + スケジュール）

## DDLルール
- 全テーブルに `created_at`, `updated_at` (TIMESTAMPTZ)
- 全テーブルに `deleted_at` (TIMESTAMPTZ) — 論理削除
- `scraped_properties` に `created_by`, `updated_by` — 監査
- 外部キーに CASCADE DELETE 禁止
- ENUM 禁止（master_options で管理）
- 企画書 §5 のスキーマ定義に従う

## 確認コマンド
```bash
psql market_intel_db -c "\dt"
psql market_intel_db -c "\d scraped_properties"
```

## 完了条件
- [ ] DDLスクリプトが `scripts/create_tables.sql` にある
- [ ] 全テーブルが作成された
- [ ] `\d` で構造確認済み

## 次の工程
→ seed.md
