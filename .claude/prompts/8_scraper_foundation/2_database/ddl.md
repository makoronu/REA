# テーブル作成（DDL）

## やること
1. market_intel_db を作成
2. `scripts/create_tables.sql` にDDLを記述・実行
3. 企画書 §5 のスキーマ定義に従う

## 対象テーブル
- master_categories / master_options / column_labels（REA踏襲）
- scraped_properties / price_history / listing_status_history
- scrape_sessions / scrape_sources

## ルール
- 全テーブルに created_at / updated_at / deleted_at
- ENUM禁止、CASCADE DELETE禁止

## 完了条件
- [ ] 全テーブル作成済み
- [ ] `\d` で構造確認済み

## 次 → seed.md
