-- 公開時必須項目データ投入
-- 実行: ssh rea-conoha "sudo -u postgres psql real_estate_db" < apply_required_for_publication_data.sql
-- 作成: 2026-01-03
-- 目的: ローカルで管理画面から設定したrequired_for_publicationデータを本番に反映

-- ============================================================================
-- 1. カラム追加（存在しない場合のみ）
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'column_labels' AND column_name = 'required_for_publication'
    ) THEN
        ALTER TABLE column_labels ADD COLUMN required_for_publication TEXT[];
        RAISE NOTICE 'column required_for_publication added';
    ELSE
        RAISE NOTICE 'column required_for_publication already exists';
    END IF;
END $$;

COMMENT ON COLUMN column_labels.required_for_publication IS '公開時必須の物件種別（NULLは任意、配列で指定種別のみ必須）';

-- ============================================================================
-- 2. propertiesテーブル（18件）
-- ============================================================================
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'property_type';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'property_name';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'postal_code';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'prefecture';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'city';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'address';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached}' WHERE table_name = 'properties' AND column_name = 'elementary_school';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached}' WHERE table_name = 'properties' AND column_name = 'junior_high_school';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'transportation';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'bus_stops';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'nearby_facilities';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'sale_price';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'tax_type';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'transaction_type';
UPDATE column_labels SET required_for_publication = '{mansion,apartment}' WHERE table_name = 'properties' AND column_name = 'management_fee';
UPDATE column_labels SET required_for_publication = '{mansion,apartment}' WHERE table_name = 'properties' AND column_name = 'repair_reserve_fund';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'current_status';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'properties' AND column_name = 'delivery_timing';

-- ============================================================================
-- 3. building_infoテーブル（13件）
-- ============================================================================
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'building_info' AND column_name = 'building_structure';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'building_info' AND column_name = 'construction_date';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'building_info' AND column_name = 'building_floors_above';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'building_info' AND column_name = 'total_units';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'building_info' AND column_name = 'building_area';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'building_info' AND column_name = 'total_floor_area';
UPDATE column_labels SET required_for_publication = '{mansion,apartment}' WHERE table_name = 'building_info' AND column_name = 'exclusive_area';
UPDATE column_labels SET required_for_publication = '{mansion,apartment}' WHERE table_name = 'building_info' AND column_name = 'room_floor';
UPDATE column_labels SET required_for_publication = '{mansion,apartment}' WHERE table_name = 'building_info' AND column_name = 'direction';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'building_info' AND column_name = 'room_count';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'building_info' AND column_name = 'room_type';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'building_info' AND column_name = 'parking_availability';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,building}' WHERE table_name = 'building_info' AND column_name = 'management_type';

-- ============================================================================
-- 4. land_infoテーブル（11件）
-- ============================================================================
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'land_info' AND column_name = 'use_district';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'land_info' AND column_name = 'city_planning';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'land_info' AND column_name = 'building_coverage_ratio';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'land_info' AND column_name = 'floor_area_ratio';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'land_info' AND column_name = 'fire_prevention_district';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'land_info' AND column_name = 'land_area';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'land_info' AND column_name = 'land_category';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'land_info' AND column_name = 'land_rights';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'land_info' AND column_name = 'setback';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'land_info' AND column_name = 'terrain';
UPDATE column_labels SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building}' WHERE table_name = 'land_info' AND column_name = 'road_info';

-- ============================================================================
-- 5. 確認クエリ
-- ============================================================================
SELECT
    table_name,
    column_name,
    required_for_publication
FROM column_labels
WHERE required_for_publication IS NOT NULL
ORDER BY table_name, column_name;
