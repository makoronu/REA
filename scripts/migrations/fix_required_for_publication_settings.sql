-- required_for_publication 設定の修正
-- 2026-01-04

-- 1. total_units から detached を除外（一戸建ては1戸なので不要）
UPDATE column_labels
SET required_for_publication = array_remove(required_for_publication, 'detached')
WHERE table_name = 'building_info' AND column_name = 'total_units';

-- 2. building_floors_below を必須から除外（地下がない物件も多い）
UPDATE column_labels
SET required_for_publication = '{}'::text[]
WHERE table_name = 'building_info' AND column_name = 'building_floors_below';

-- 確認
SELECT table_name, column_name, required_for_publication
FROM column_labels
WHERE table_name = 'building_info'
  AND column_name IN ('total_units', 'building_floors_below');
