-- city_planning カラムを INTEGER → JSONB に変更
-- 理由: 境界線上の土地では複数の都市計画区域にまたがる場合がある

-- 1. 既存データをバックアップ（確認用）
SELECT id, city_planning
FROM land_info
WHERE city_planning IS NOT NULL AND deleted_at IS NULL
LIMIT 10;

-- 2. カラム型変更（INTEGER → JSONB）
-- 既存の単一値を配列に変換
ALTER TABLE land_info
ALTER COLUMN city_planning TYPE jsonb
USING CASE
    WHEN city_planning IS NULL THEN NULL
    ELSE jsonb_build_array(city_planning)
END;

-- 3. 変更後確認
SELECT id, city_planning
FROM land_info
WHERE city_planning IS NOT NULL AND deleted_at IS NULL
LIMIT 10;

-- 4. column_labels の input_type を multi_select に変更
UPDATE column_labels
SET input_type = 'multi_select'
WHERE table_name = 'land_info'
  AND column_name = 'city_planning';

-- 確認
SELECT column_name, input_type
FROM column_labels
WHERE table_name = 'land_info' AND column_name = 'city_planning';
