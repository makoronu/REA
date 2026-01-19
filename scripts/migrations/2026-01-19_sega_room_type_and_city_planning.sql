-- SegA: 間取り「不明」追加 + 都市計画api_aliases設定
-- 日付: 2026-01-19
-- 作業者: Claude

-- =============================================================================
-- 1. 間取り「不明」追加
-- =============================================================================
-- 現在: 1:R,2:K,3:DK,4:LDK,5:SLDK,6:その他
-- 変更後: 1:R,2:K,3:DK,4:LDK,5:SLDK,6:その他,7:不明

UPDATE column_labels
SET options = '1:R,2:K,3:DK,4:LDK,5:SLDK,6:その他,7:不明'
WHERE column_name = 'room_type'
  AND table_name = 'building_info';

-- =============================================================================
-- 2. 都市計画 api_aliases設定
-- =============================================================================
-- reinfolib APIから返される区域区分名をマッピング

-- 市街化区域
UPDATE master_options
SET api_aliases = ARRAY['市街化区域']
WHERE option_code = 'rea_1'
  AND category_id = (SELECT id FROM master_categories WHERE category_code = 'city_planning');

-- 市街化調整区域
UPDATE master_options
SET api_aliases = ARRAY['市街化調整区域']
WHERE option_code = 'rea_2'
  AND category_id = (SELECT id FROM master_categories WHERE category_code = 'city_planning');

-- 非線引区域（都市計画区域内で線引きされていない区域）
UPDATE master_options
SET api_aliases = ARRAY['非線引き区域', '非線引区域', '区域区分非設定']
WHERE option_code = 'rea_3'
  AND category_id = (SELECT id FROM master_categories WHERE category_code = 'city_planning');

-- 都市計画区域外
UPDATE master_options
SET api_aliases = ARRAY['都市計画区域外']
WHERE option_code = 'rea_4'
  AND category_id = (SELECT id FROM master_categories WHERE category_code = 'city_planning');

-- =============================================================================
-- 確認クエリ
-- =============================================================================

-- 間取りオプション確認
SELECT column_name, options
FROM column_labels
WHERE column_name = 'room_type';

-- 都市計画api_aliases確認
SELECT mo.option_code, mo.option_value, mo.api_aliases
FROM master_options mo
JOIN master_categories mc ON mo.category_id = mc.id
WHERE mc.category_code = 'city_planning'
  AND mo.source = 'rea';
