-- 法令制限チェック項目用カラム追加
-- 実行: psql -U rea_user -d rea_db -f add_legal_regulations_checked.sql

-- 1. land_infoテーブルにJSONBカラム追加
ALTER TABLE land_info
ADD COLUMN IF NOT EXISTS legal_regulations_checked JSONB DEFAULT '[]'::jsonb;

-- 2. 防火地域カラム追加
ALTER TABLE land_info
ADD COLUMN IF NOT EXISTS fire_prevention_area VARCHAR(50);

-- 3. 高度地区カラム追加
ALTER TABLE land_info
ADD COLUMN IF NOT EXISTS height_district VARCHAR(100);

-- 4. 景観地区カラム追加
ALTER TABLE land_info
ADD COLUMN IF NOT EXISTS landscape_district BOOLEAN DEFAULT FALSE;

-- 5. 地区計画名カラム追加
ALTER TABLE land_info
ADD COLUMN IF NOT EXISTS district_plan_name VARCHAR(200);

-- 6. column_labelsにエントリ追加
INSERT INTO column_labels (table_name, column_name, label_ja, data_type, field_group, display_order, is_visible)
VALUES
    ('land_info', 'legal_regulations_checked', '法令制限（チェック）', 'jsonb', '法令制限', 100, true),
    ('land_info', 'fire_prevention_area', '防火地域', 'varchar', '法令制限', 101, true),
    ('land_info', 'height_district', '高度地区', 'varchar', '法令制限', 102, true),
    ('land_info', 'landscape_district', '景観地区', 'boolean', '法令制限', 103, true),
    ('land_info', 'district_plan_name', '地区計画', 'varchar', '法令制限', 104, true)
ON CONFLICT (table_name, column_name) DO UPDATE SET
    label_ja = EXCLUDED.label_ja,
    field_group = EXCLUDED.field_group,
    display_order = EXCLUDED.display_order;

-- 7. 防火地域の選択肢をmaster_optionsに追加
INSERT INTO master_options (source, master_category_code, option_code, option_name, sort_order, is_active)
VALUES
    ('rea', 'fire_prevention_area', '1', '防火地域', 1, true),
    ('rea', 'fire_prevention_area', '2', '準防火地域', 2, true),
    ('rea', 'fire_prevention_area', '3', '指定なし', 3, true)
ON CONFLICT DO NOTHING;

COMMENT ON COLUMN land_info.legal_regulations_checked IS '重要事項説明書の法令制限チェック項目（JSON配列）';
COMMENT ON COLUMN land_info.fire_prevention_area IS '防火地域区分';
COMMENT ON COLUMN land_info.height_district IS '高度地区';
COMMENT ON COLUMN land_info.landscape_district IS '景観地区に該当するか';
COMMENT ON COLUMN land_info.district_plan_name IS '地区計画名';
