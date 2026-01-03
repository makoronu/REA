-- property_locationsテーブル削除
-- 作成日: 2026-01-03
-- 理由:
--   1. propertiesテーブルに住所カラムが既に存在（重複）
--   2. property_locationsは7件のみ（全てpropertiesと同一データ）
--   3. column_labelsに未登録（メタデータ駆動外）
--   4. 紛らわしさ解消のため削除

-- 事前確認（データ損失がないことを確認）
-- SELECT COUNT(*) FROM property_locations;  -- 7件
-- SELECT COUNT(*) FROM properties;          -- 2370件

-- インデックス削除
DROP INDEX IF EXISTS idx_property_locations_geom;
DROP INDEX IF EXISTS idx_property_locations_deleted_at;

-- テーブル削除
DROP TABLE IF EXISTS property_locations;
