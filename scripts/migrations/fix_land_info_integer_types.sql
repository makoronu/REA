-- land_info 7カラムをINTEGERに復元
-- 根本原因: metadata.py が source='rea' を返していたため rea_1 等が保存されていた
-- 修正: source='homes' に変更済み（INTEGER コードを返す）

-- 既存データはクリア（本番から復旧するため）
-- 型変換エラーを回避

-- 1. setback: VARCHAR → INTEGER
ALTER TABLE land_info
ALTER COLUMN setback TYPE INTEGER
USING NULL;

-- 2. terrain: VARCHAR → INTEGER
ALTER TABLE land_info
ALTER COLUMN terrain TYPE INTEGER
USING NULL;

-- 3. city_planning: JSONB → INTEGER
ALTER TABLE land_info
ALTER COLUMN city_planning TYPE INTEGER
USING NULL;

-- 4. land_category: JSONB → INTEGER
ALTER TABLE land_info
ALTER COLUMN land_category TYPE INTEGER
USING NULL;

-- 5. land_rights: VARCHAR → INTEGER
ALTER TABLE land_info
ALTER COLUMN land_rights TYPE INTEGER
USING NULL;

-- 6. land_transaction_notice: VARCHAR → INTEGER
ALTER TABLE land_info
ALTER COLUMN land_transaction_notice TYPE INTEGER
USING NULL;

-- 7. land_area_measurement: VARCHAR → INTEGER
ALTER TABLE land_info
ALTER COLUMN land_area_measurement TYPE INTEGER
USING NULL;

-- 確認
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'land_info'
AND column_name IN ('setback', 'terrain', 'city_planning', 'land_category', 'land_rights', 'land_transaction_notice', 'land_area_measurement')
ORDER BY column_name;
