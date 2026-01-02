-- Step 1: 監査カラム追加マイグレーション
-- 実行日: 2026-01-02
-- 目的: プロトコル準拠のため、9テーブルに監査カラムを追加
--
-- 追加カラム:
--   - created_by VARCHAR(100): 作成者
--   - updated_by VARCHAR(100): 更新者
--   - deleted_at TIMESTAMPTZ: 論理削除日時

-- 1. properties
ALTER TABLE properties ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 2. building_info
ALTER TABLE building_info ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE building_info ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE building_info ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 3. land_info
ALTER TABLE land_info ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE land_info ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE land_info ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 4. property_images
ALTER TABLE property_images ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE property_images ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE property_images ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 5. property_equipment
ALTER TABLE property_equipment ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE property_equipment ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE property_equipment ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 6. property_locations
ALTER TABLE property_locations ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE property_locations ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE property_locations ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 7. property_registries
ALTER TABLE property_registries ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE property_registries ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE property_registries ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 8. column_labels
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- 9. equipment_master
ALTER TABLE equipment_master ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE equipment_master ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE equipment_master ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- インデックス作成（deleted_at検索用）
CREATE INDEX IF NOT EXISTS idx_properties_deleted_at ON properties(deleted_at);
CREATE INDEX IF NOT EXISTS idx_building_info_deleted_at ON building_info(deleted_at);
CREATE INDEX IF NOT EXISTS idx_land_info_deleted_at ON land_info(deleted_at);
CREATE INDEX IF NOT EXISTS idx_property_images_deleted_at ON property_images(deleted_at);
CREATE INDEX IF NOT EXISTS idx_property_equipment_deleted_at ON property_equipment(deleted_at);
CREATE INDEX IF NOT EXISTS idx_property_locations_deleted_at ON property_locations(deleted_at);
CREATE INDEX IF NOT EXISTS idx_property_registries_deleted_at ON property_registries(deleted_at);
CREATE INDEX IF NOT EXISTS idx_column_labels_deleted_at ON column_labels(deleted_at);
CREATE INDEX IF NOT EXISTS idx_equipment_master_deleted_at ON equipment_master(deleted_at);

-- ロールバック用（必要な場合）
-- ALTER TABLE properties DROP COLUMN IF EXISTS created_by;
-- ALTER TABLE properties DROP COLUMN IF EXISTS updated_by;
-- ALTER TABLE properties DROP COLUMN IF EXISTS deleted_at;
-- (他テーブルも同様)
