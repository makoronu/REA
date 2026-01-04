-- use_district の rea_* 形式を数値形式に変換
-- 例: ["rea_5"] → [5], ["rea_99"] → [99]

-- 変換前の確認
SELECT COUNT(*) as total_rea_format
FROM land_info
WHERE use_district IS NOT NULL
  AND use_district::text LIKE '%rea_%'
  AND deleted_at IS NULL;

-- 変換実行
UPDATE land_info
SET use_district = (
  SELECT jsonb_agg(
    CASE
      WHEN elem::text LIKE '"rea_%"'
      THEN (REGEXP_REPLACE(elem::text, '"rea_(.*)"', '\1'))::int
      ELSE (TRIM(BOTH '"' FROM elem::text))::int
    END
  )
  FROM jsonb_array_elements(use_district) elem
)
WHERE use_district IS NOT NULL
  AND use_district::text LIKE '%rea_%'
  AND deleted_at IS NULL;

-- 変換後の確認
SELECT COUNT(*) as remaining_rea_format
FROM land_info
WHERE use_district IS NOT NULL
  AND use_district::text LIKE '%rea_%'
  AND deleted_at IS NULL;
