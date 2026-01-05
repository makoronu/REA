-- ============================================================================
-- 土地（land）物件のrequired_for_publication設定追加
-- ============================================================================
-- 実行: ssh rea-conoha "sudo -u postgres psql real_estate_db" < add_land_to_required_for_publication.sql
-- 作成: 2026-01-05
-- 目的: 土地物件の公開時バリデーションを有効化
-- 背景: landがrequired_for_publication配列に含まれていなかったため、
--       土地物件の公開時に必須項目チェックがスキップされていた
-- 適用済み: 2026-01-05 本番DB
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. propertiesテーブル - 既存配列にlandを追加
-- ============================================================================
-- 基本情報
UPDATE column_labels SET required_for_publication = array_append(required_for_publication, 'land')
WHERE table_name = 'properties' AND column_name = 'property_type'
  AND required_for_publication IS NOT NULL AND NOT ('land' = ANY(required_for_publication));

UPDATE column_labels SET required_for_publication = array_append(required_for_publication, 'land')
WHERE table_name = 'properties' AND column_name = 'property_name'
  AND required_for_publication IS NOT NULL AND NOT ('land' = ANY(required_for_publication));

-- 住所情報
UPDATE column_labels SET required_for_publication = array_append(required_for_publication, 'land')
WHERE table_name = 'properties' AND column_name = 'postal_code'
  AND required_for_publication IS NOT NULL AND NOT ('land' = ANY(required_for_publication));

UPDATE column_labels SET required_for_publication = array_append(required_for_publication, 'land')
WHERE table_name = 'properties' AND column_name = 'prefecture'
  AND required_for_publication IS NOT NULL AND NOT ('land' = ANY(required_for_publication));

UPDATE column_labels SET required_for_publication = array_append(required_for_publication, 'land')
WHERE table_name = 'properties' AND column_name = 'city'
  AND required_for_publication IS NOT NULL AND NOT ('land' = ANY(required_for_publication));

UPDATE column_labels SET required_for_publication = array_append(required_for_publication, 'land')
WHERE table_name = 'properties' AND column_name = 'address'
  AND required_for_publication IS NOT NULL AND NOT ('land' = ANY(required_for_publication));

UPDATE column_labels SET required_for_publication = array_append(required_for_publication, 'land')
WHERE table_name = 'properties' AND column_name = 'tax_type'
  AND required_for_publication IS NOT NULL AND NOT ('land' = ANY(required_for_publication));

-- ============================================================================
-- 2. propertiesテーブル - NULLの場合は新規設定
-- ============================================================================
UPDATE column_labels
SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building,land}'
WHERE table_name = 'properties' AND column_name = 'sale_price'
  AND (required_for_publication IS NULL OR NOT ('land' = ANY(required_for_publication)));

UPDATE column_labels
SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building,land}'
WHERE table_name = 'properties' AND column_name = 'transaction_type'
  AND (required_for_publication IS NULL OR NOT ('land' = ANY(required_for_publication)));

UPDATE column_labels
SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building,land}'
WHERE table_name = 'properties' AND column_name = 'current_status'
  AND (required_for_publication IS NULL OR NOT ('land' = ANY(required_for_publication)));

UPDATE column_labels
SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building,land}'
WHERE table_name = 'properties' AND column_name = 'delivery_timing'
  AND (required_for_publication IS NULL OR NOT ('land' = ANY(required_for_publication)));

-- ============================================================================
-- 3. land_infoテーブル - 既存配列にlandを追加
-- ============================================================================
UPDATE column_labels SET required_for_publication = array_append(required_for_publication, 'land')
WHERE table_name = 'land_info' AND column_name = 'building_coverage_ratio'
  AND required_for_publication IS NOT NULL AND NOT ('land' = ANY(required_for_publication));

UPDATE column_labels SET required_for_publication = array_append(required_for_publication, 'land')
WHERE table_name = 'land_info' AND column_name = 'floor_area_ratio'
  AND required_for_publication IS NOT NULL AND NOT ('land' = ANY(required_for_publication));

UPDATE column_labels SET required_for_publication = array_append(required_for_publication, 'land')
WHERE table_name = 'land_info' AND column_name = 'fire_prevention_district'
  AND required_for_publication IS NOT NULL AND NOT ('land' = ANY(required_for_publication));

UPDATE column_labels SET required_for_publication = array_append(required_for_publication, 'land')
WHERE table_name = 'land_info' AND column_name = 'setback'
  AND required_for_publication IS NOT NULL AND NOT ('land' = ANY(required_for_publication));

-- ============================================================================
-- 4. land_infoテーブル - NULLの場合は新規設定
-- ============================================================================
-- 全物件種別で必須
UPDATE column_labels
SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building,land}'
WHERE table_name = 'land_info' AND column_name = 'use_district'
  AND (required_for_publication IS NULL OR NOT ('land' = ANY(required_for_publication)));

UPDATE column_labels
SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building,land}'
WHERE table_name = 'land_info' AND column_name = 'city_planning'
  AND (required_for_publication IS NULL OR NOT ('land' = ANY(required_for_publication)));

-- 土地物件のみ必須
UPDATE column_labels
SET required_for_publication = '{land}'
WHERE table_name = 'land_info' AND column_name = 'land_area'
  AND (required_for_publication IS NULL OR NOT ('land' = ANY(required_for_publication)));

UPDATE column_labels
SET required_for_publication = '{land}'
WHERE table_name = 'land_info' AND column_name = 'land_category'
  AND (required_for_publication IS NULL OR NOT ('land' = ANY(required_for_publication)));

UPDATE column_labels
SET required_for_publication = '{land}'
WHERE table_name = 'land_info' AND column_name = 'land_rights'
  AND (required_for_publication IS NULL OR NOT ('land' = ANY(required_for_publication)));

UPDATE column_labels
SET required_for_publication = '{land}'
WHERE table_name = 'land_info' AND column_name = 'terrain'
  AND (required_for_publication IS NULL OR NOT ('land' = ANY(required_for_publication)));

UPDATE column_labels
SET required_for_publication = '{land}'
WHERE table_name = 'land_info' AND column_name = 'road_info'
  AND (required_for_publication IS NULL OR NOT ('land' = ANY(required_for_publication)));

COMMIT;

-- ============================================================================
-- 5. 確認クエリ
-- ============================================================================
-- land が含まれるフィールド一覧
SELECT
    table_name,
    column_name,
    japanese_label,
    required_for_publication
FROM column_labels
WHERE 'land' = ANY(required_for_publication)
ORDER BY table_name, column_name;

-- land物件（property_type='land'）の必須フィールド数
SELECT COUNT(*) as required_field_count
FROM column_labels
WHERE 'land' = ANY(required_for_publication);
