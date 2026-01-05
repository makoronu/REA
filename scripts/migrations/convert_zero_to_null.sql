-- =====================================================
-- 0 → NULL 変換マイグレーション
-- 対象: 公開前確認ステータス（92件）
-- 作成日: 2026-01-04
-- =====================================================

BEGIN;

-- =====================================================
-- Phase 1: NOT NULL制約を削除
-- =====================================================

-- properties テーブル
ALTER TABLE properties ALTER COLUMN priority_score DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN sale_price DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN price_per_tsubo DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN yield_rate DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN current_yield DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN management_fee DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN repair_reserve_fund DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN repair_reserve_fund_base DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN parking_fee DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN housing_insurance DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN brokerage_fee DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN commission_split_ratio DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN current_status DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN transaction_type DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN delivery_timing DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN price_status DROP NOT NULL;
ALTER TABLE properties ALTER COLUMN tax_type DROP NOT NULL;

-- land_info テーブル
ALTER TABLE land_info ALTER COLUMN land_area DROP NOT NULL;
ALTER TABLE land_info ALTER COLUMN building_coverage_ratio DROP NOT NULL;
ALTER TABLE land_info ALTER COLUMN floor_area_ratio DROP NOT NULL;
ALTER TABLE land_info ALTER COLUMN land_rent DROP NOT NULL;
ALTER TABLE land_info ALTER COLUMN private_road_area DROP NOT NULL;
ALTER TABLE land_info ALTER COLUMN setback_amount DROP NOT NULL;

-- building_info テーブル
ALTER TABLE building_info ALTER COLUMN building_floors_above DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN building_floors_below DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN total_units DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN total_site_area DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN building_area DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN total_floor_area DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN exclusive_area DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN balcony_area DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN room_floor DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN room_count DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN parking_capacity DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN parking_distance DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN building_structure DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN direction DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN room_type DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN parking_availability DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN parking_type DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN area_measurement_type DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN building_manager DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN management_type DROP NOT NULL;
ALTER TABLE building_info ALTER COLUMN management_association DROP NOT NULL;

-- =====================================================
-- Phase 2: 0 → NULL 変換（公開前確認のみ）
-- =====================================================

-- properties テーブル
-- ※ sale_price, current_status, transaction_type, price_status, tax_type は0件なのでスキップ可
UPDATE properties SET
  priority_score = NULLIF(priority_score, 0),
  price_per_tsubo = NULLIF(price_per_tsubo, 0),
  yield_rate = NULLIF(yield_rate, 0),
  current_yield = NULLIF(current_yield, 0),
  management_fee = NULLIF(management_fee, 0),
  repair_reserve_fund = NULLIF(repair_reserve_fund, 0),
  repair_reserve_fund_base = NULLIF(repair_reserve_fund_base, 0),
  parking_fee = NULLIF(parking_fee, 0),
  housing_insurance = NULLIF(housing_insurance, 0),
  brokerage_fee = NULLIF(brokerage_fee, 0),
  commission_split_ratio = NULLIF(commission_split_ratio, 0),
  delivery_timing = NULLIF(delivery_timing, 0)
WHERE publication_status = '公開前確認';

-- land_info テーブル
-- ※ private_road_area, setback_amount, land_rent は0が有効な場合があるが、
--   公開前確認ステータスでは「未入力」の意味なのでNULLに変換
UPDATE land_info SET
  land_area = NULLIF(land_area, 0),
  building_coverage_ratio = NULLIF(building_coverage_ratio, 0),
  floor_area_ratio = NULLIF(floor_area_ratio, 0),
  land_rent = NULLIF(land_rent, 0),
  private_road_area = NULLIF(private_road_area, 0),
  setback_amount = NULLIF(setback_amount, 0)
WHERE property_id IN (SELECT id FROM properties WHERE publication_status = '公開前確認');

-- building_info テーブル
-- ※ building_floors_below, balcony_area, parking_capacity は0が有効だが、
--   公開前確認ステータスでは「未入力」の意味なのでNULLに変換
UPDATE building_info SET
  building_floors_above = NULLIF(building_floors_above, 0),
  building_floors_below = NULLIF(building_floors_below, 0),
  total_units = NULLIF(total_units, 0),
  total_site_area = NULLIF(total_site_area, 0),
  building_area = NULLIF(building_area, 0),
  total_floor_area = NULLIF(total_floor_area, 0),
  exclusive_area = NULLIF(exclusive_area, 0),
  balcony_area = NULLIF(balcony_area, 0),
  room_floor = NULLIF(room_floor, 0),
  room_count = NULLIF(room_count, 0),
  parking_capacity = NULLIF(parking_capacity, 0),
  parking_distance = NULLIF(parking_distance, 0),
  building_structure = NULLIF(building_structure, 0),
  direction = NULLIF(direction, 0),
  room_type = NULLIF(room_type, 0),
  parking_availability = NULLIF(parking_availability, 0),
  parking_type = NULLIF(parking_type, 0),
  area_measurement_type = NULLIF(area_measurement_type, 0),
  building_manager = NULLIF(building_manager, 0),
  management_type = NULLIF(management_type, 0),
  management_association = NULLIF(management_association, 0)
WHERE property_id IN (SELECT id FROM properties WHERE publication_status = '公開前確認');

COMMIT;

-- =====================================================
-- 検証クエリ
-- =====================================================
SELECT 'properties' as tbl,
  COUNT(*) FILTER (WHERE management_fee IS NULL) as null_management_fee,
  COUNT(*) FILTER (WHERE management_fee = 0) as zero_management_fee
FROM properties WHERE publication_status = '公開前確認';

SELECT 'land_info' as tbl,
  COUNT(*) FILTER (WHERE land_area IS NULL) as null_land_area,
  COUNT(*) FILTER (WHERE land_area = 0) as zero_land_area
FROM land_info li JOIN properties p ON li.property_id = p.id
WHERE p.publication_status = '公開前確認';

SELECT 'building_info' as tbl,
  COUNT(*) FILTER (WHERE exclusive_area IS NULL) as null_exclusive_area,
  COUNT(*) FILTER (WHERE exclusive_area = 0) as zero_exclusive_area
FROM building_info bi JOIN properties p ON bi.property_id = p.id
WHERE p.publication_status = '公開前確認';
