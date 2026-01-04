-- publication_status: 公開不合格 → 公開前確認 に変更
-- 2026-01-04

-- 1. master_options: option_code と option_value を変更
UPDATE master_options mo
SET option_code = 'pre_check', option_value = '公開前確認'
FROM master_categories mc
WHERE mo.category_id = mc.id
  AND mc.category_code = 'publication_status'
  AND mo.option_code = 'failed';

-- 2. properties: 既存データの公開不合格 → 公開前確認 に変換
UPDATE properties
SET publication_status = '公開前確認'
WHERE publication_status = '公開不合格';

-- 確認
SELECT option_code, option_value
FROM master_options mo
JOIN master_categories mc ON mo.category_id = mc.id
WHERE mc.category_code = 'publication_status';
