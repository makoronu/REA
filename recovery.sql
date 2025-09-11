-- REAデータベース完全復旧SQL
-- 26テーブル分割構造（ドキュメント準拠版）

-- ========================================
-- 1. データベース作成（必要な場合）
-- ========================================
-- CREATE DATABASE real_estate_db OWNER rea_user;

-- ========================================
-- 2. ENUM型定義（26種類）
-- ========================================
DROP TYPE IF EXISTS investment_property_enum CASCADE;
CREATE TYPE investment_property_enum AS ENUM ('通常物件', '投資用物件');

DROP TYPE IF EXISTS property_name_public_enum CASCADE;
CREATE TYPE property_name_public_enum AS ENUM ('非公開', '公開');

DROP TYPE IF EXISTS topography_enum CASCADE;
CREATE TYPE topography_enum AS ENUM ('平坦', '高台', '低地', 'ひな壇', '傾斜地', '不整形地', 'その他');

DROP TYPE IF EXISTS land_area_measurement_enum CASCADE;
CREATE TYPE land_area_measurement_enum AS ENUM ('公簿', '実測', '私測');

DROP TYPE IF EXISTS setback_enum CASCADE;
CREATE TYPE setback_enum AS ENUM ('不要', '要', 'セットバック済');

DROP TYPE IF EXISTS road_frontage_status_enum CASCADE;
CREATE TYPE road_frontage_status_enum AS ENUM ('一方', '二方（角地）', '三方', '四方', '接道なし');

DROP TYPE IF EXISTS road_direction_enum CASCADE;
CREATE TYPE road_direction_enum AS ENUM ('北', '北東', '東', '南東', '南', '南西', '西', '北西');

DROP TYPE IF EXISTS road_type_enum CASCADE;
CREATE TYPE road_type_enum AS ENUM ('国道', '都道府県道', '市区町村道', '私道', '位置指定道路', '開発道路', 'その他');

DROP TYPE IF EXISTS designated_road_enum CASCADE;
CREATE TYPE designated_road_enum AS ENUM ('無', '有');

DROP TYPE IF EXISTS land_transaction_notice_enum CASCADE;
CREATE TYPE land_transaction_notice_enum AS ENUM ('不要', '要', '届出済');

DROP TYPE IF EXISTS building_area_measurement_enum CASCADE;
CREATE TYPE building_area_measurement_enum AS ENUM ('壁芯', '内法', '登記簿');

DROP TYPE IF EXISTS building_manager_enum CASCADE;
CREATE TYPE building_manager_enum AS ENUM ('常駐', '日勤', '巡回', '自主管理', '無');

DROP TYPE IF EXISTS management_association_enum CASCADE;
CREATE TYPE management_association_enum AS ENUM ('無', '有');

DROP TYPE IF EXISTS room_type_enum CASCADE;
CREATE TYPE room_type_enum AS ENUM ('洋室', '和室', '洋和室', 'DK', 'LDK', 'L', 'D', 'K', 'その他');

DROP TYPE IF EXISTS floor_plan_type_enum CASCADE;
CREATE TYPE floor_plan_type_enum AS ENUM ('R', 'K', 'DK', 'LDK', 'S', 'L', 'D', 'LK', 'SDK', 'SLDK', 'その他');

DROP TYPE IF EXISTS price_status_enum CASCADE;
CREATE TYPE price_status_enum AS ENUM ('確定', '相談', '応相談', '変更可');

DROP TYPE IF EXISTS tax_enum CASCADE;
CREATE TYPE tax_enum AS ENUM ('税込', '税抜', '非課税');

DROP TYPE IF EXISTS contract_period_type_enum CASCADE;
CREATE TYPE contract_period_type_enum AS ENUM ('普通借家契約', '定期借家契約');

DROP TYPE IF EXISTS contract_type_enum CASCADE;
CREATE TYPE contract_type_enum AS ENUM ('賃貸', '売買', '賃貸・売買両方可');

DROP TYPE IF EXISTS current_status_enum CASCADE;
CREATE TYPE current_status_enum AS ENUM ('空室', '空予定', '賃貸中', '居住中', 'その他');

DROP TYPE IF EXISTS move_in_timing_enum CASCADE;
CREATE TYPE move_in_timing_enum AS ENUM ('即時', '相談', '期日指定');

DROP TYPE IF EXISTS move_in_period_enum CASCADE;
CREATE TYPE move_in_period_enum AS ENUM ('上旬', '中旬', '下旬');

DROP TYPE IF EXISTS tenant_placement_enum CASCADE;
CREATE TYPE tenant_placement_enum AS ENUM ('不可', '可');

DROP TYPE IF EXISTS parking_type_enum CASCADE;
CREATE TYPE parking_type_enum AS ENUM ('無', '有（無料）', '有（有料）', '近隣（無料）', '近隣（有料）');

DROP TYPE IF EXISTS image_type_enum CASCADE;
CREATE TYPE image_type_enum AS ENUM ('外観', '間取図', '居室', 'キッチン', '風呂', 'トイレ', '洗面', '設備', '玄関', 'バルコニー', '眺望', '共用部', '周辺環境', 'その他');

DROP TYPE IF EXISTS property_publication_type_enum CASCADE;
CREATE TYPE property_publication_type_enum AS ENUM ('一般公開', '会員限定', '自社限定', '非公開');

-- ========================================
-- 3. メインテーブル作成（26テーブル - ドキュメント準拠）
-- ========================================

-- 1. properties（基本情報）- 12カラム
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    homes_record_id VARCHAR(50) UNIQUE,
    company_property_number VARCHAR(500),
    status VARCHAR(100),
    property_type VARCHAR(100),
    investment_property investment_property_enum,
    building_property_name VARCHAR(500),
    building_name_kana VARCHAR(500),
    property_name_public property_name_public_enum,
    total_units INTEGER,
    vacant_units INTEGER,
    vacant_units_detail TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    building_structure_id VARCHAR(20),
    current_status_id VARCHAR(30),
    property_type_id VARCHAR(40),
    zoning_district_id VARCHAR(40),
    land_rights_id VARCHAR(30)
);

-- 2. properties_pricing（価格・収益）- 16カラム
CREATE TABLE IF NOT EXISTS properties_pricing (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    rent_price INTEGER,
    price_status price_status_enum,
    tax tax_enum,
    tax_amount tax_enum,
    price_per_tsubo INTEGER,
    common_management_fee INTEGER,
    common_management_fee_tax tax_enum,
    full_occupancy_yield INTEGER,
    current_yield INTEGER,
    housing_insurance INTEGER,
    land_rent INTEGER,
    repair_reserve_fund INTEGER,
    repair_reserve_fund_base INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id)
);

-- 3. properties_location（所在地情報）- 11カラム
CREATE TABLE IF NOT EXISTS properties_location (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    postal_code VARCHAR(8),
    address_code INTEGER,
    address_name VARCHAR(500),
    address_detail_public TEXT,
    address_detail_private TEXT,
    latitude_longitude VARCHAR(500),
    other_transportation VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id)
);

-- 4. properties_transportation（交通情報）- 15カラム
CREATE TABLE IF NOT EXISTS properties_transportation (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    train_line_1 VARCHAR(100),
    station_1 VARCHAR(100),
    bus_stop_name_1 VARCHAR(100),
    bus_time_1 INTEGER,
    walking_distance_1 INTEGER,
    train_line_2 VARCHAR(100),
    station_2 VARCHAR(100),
    bus_stop_name_2 VARCHAR(100),
    bus_time_2 INTEGER,
    walking_distance_2 INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id)
);

-- 5. properties_images（画像情報）- 94カラム
CREATE TABLE IF NOT EXISTS properties_images (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    image_type_1 image_type_enum,
    image_comment_1 TEXT,
    local_file_name_1 VARCHAR(500),
    local_file_name_2 VARCHAR(500),
    image_type_2 image_type_enum,
    image_comment_2 TEXT,
    local_file_name_3 VARCHAR(500),
    image_type_3 image_type_enum,
    image_comment_3 TEXT,
    local_file_name_4 VARCHAR(500),
    image_type_4 image_type_enum,
    image_comment_4 TEXT,
    local_file_name_5 VARCHAR(500),
    image_type_5 image_type_enum,
    image_comment_5 TEXT,
    local_file_name_6 VARCHAR(500),
    image_type_6 image_type_enum,
    image_comment_6 TEXT,
    affiliated_group VARCHAR(500),
    facilities_conditions VARCHAR(500),
    recommendation_points INTEGER,
    move_in_consultation move_in_timing_enum,
    image_type_7 image_type_enum,
    image_comment_7 TEXT,
    local_file_name_7 VARCHAR(500),
    local_file_name_8 VARCHAR(500),
    image_type_8 image_type_enum,
    image_comment_8 TEXT,
    local_file_name_9 VARCHAR(500),
    image_type_9 image_type_enum,
    image_comment_9 TEXT,
    local_file_name_10 VARCHAR(500),
    image_type_10 image_type_enum,
    image_comment_10 TEXT,
    local_file_name_11 VARCHAR(500),
    image_type_11 image_type_enum,
    image_comment_11 TEXT,
    local_file_name_12 VARCHAR(500),
    image_type_12 image_type_enum,
    image_comment_12 TEXT,
    local_file_name_13 VARCHAR(500),
    image_type_13 image_type_enum,
    image_comment_13 TEXT,
    local_file_name_14 VARCHAR(500),
    image_type_14 image_type_enum,
    image_comment_14 TEXT,
    local_file_name_15 VARCHAR(500),
    image_type_15 image_type_enum,
    image_comment_15 TEXT,
    local_file_name_16 VARCHAR(500),
    image_type_16 image_type_enum,
    image_comment_16 TEXT,
    local_file_name_17 VARCHAR(500),
    image_type_17 image_type_enum,
    image_comment_17 TEXT,
    local_file_name_18 VARCHAR(500),
    image_type_18 image_type_enum,
    image_comment_18 TEXT,
    local_file_name_19 VARCHAR(500),
    image_type_19 image_type_enum,
    image_comment_19 TEXT,
    local_file_name_20 VARCHAR(500),
    image_type_20 image_type_enum,
    image_comment_20 TEXT,
    local_file_name_21 VARCHAR(500),
    image_type_21 image_type_enum,
    image_comment_21 TEXT,
    local_file_name_22 VARCHAR(500),
    image_type_22 image_type_enum,
    image_comment_22 TEXT,
    local_file_name_23 VARCHAR(500),
    image_type_23 image_type_enum,
    image_comment_23 TEXT,
    local_file_name_24 VARCHAR(500),
    image_type_24 image_type_enum,
    image_comment_24 TEXT,
    local_file_name_25 VARCHAR(500),
    image_type_25 image_type_enum,
    image_comment_25 TEXT,
    local_file_name_26 VARCHAR(500),
    image_type_26 image_type_enum,
    image_comment_26 TEXT,
    local_file_name_27 VARCHAR(500),
    image_type_27 image_type_enum,
    image_comment_27 TEXT,
    local_file_name_28 VARCHAR(500),
    image_type_28 image_type_enum,
    image_comment_28 TEXT,
    local_file_name_29 VARCHAR(500),
    image_type_29 image_type_enum,
    image_comment_29 TEXT,
    local_file_name_30 VARCHAR(500),
    image_type_30 image_type_enum,
    image_comment_30 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id)
);

-- 6. properties_building（建物情報）- 37カラム
CREATE TABLE IF NOT EXISTS properties_building (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    building_structure VARCHAR(100),
    building_area_measurement building_area_measurement_enum,
    building_exclusive_area NUMERIC(10,2),
    total_site_area NUMERIC(10,2),
    total_floor_area NUMERIC(10,2),
    building_area NUMERIC(10,2),
    building_floors_above INTEGER,
    building_floors_below INTEGER,
    construction_date DATE,
    building_manager building_manager_enum,
    management_type VARCHAR(100),
    management_association management_association_enum,
    management_company VARCHAR(500),
    room_floor INTEGER,
    balcony_area NUMERIC(10,2),
    direction road_direction_enum,
    room_count INTEGER,
    room_type room_type_enum,
    floor_plan_notes TEXT,
    property_features TEXT,
    notes TEXT,
    url VARCHAR(500),
    internal_memo TEXT,
    common_management_fee INTEGER,
    common_management_fee_tax tax_enum,
    parking_fee INTEGER,
    parking_fee_tax tax_enum,
    parking_type parking_type_enum,
    parking_distance INTEGER,
    parking_available INTEGER,
    parking_notes TEXT,
    energy_consumption_min INTEGER,
    energy_consumption_max INTEGER,
    insulation_performance_min INTEGER,
    insulation_performance_max INTEGER,
    utility_cost_min INTEGER,
    utility_cost_max INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id)
);

-- 7. properties_floor_plans（間取り情報）- 45カラム
CREATE TABLE IF NOT EXISTS properties_floor_plans (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    floor_plan_type_1 floor_plan_type_enum,
    floor_plan_tatami_1 INTEGER,
    floor_plan_floor_1 INTEGER,
    floor_plan_rooms_1 INTEGER,
    floor_plan_type_2 floor_plan_type_enum,
    floor_plan_tatami_2 INTEGER,
    floor_plan_floor_2 INTEGER,
    floor_plan_rooms_2 INTEGER,
    floor_plan_type_3 floor_plan_type_enum,
    floor_plan_tatami_3 INTEGER,
    floor_plan_floor_3 INTEGER,
    floor_plan_rooms_3 INTEGER,
    floor_plan_type_4 floor_plan_type_enum,
    floor_plan_tatami_4 INTEGER,
    floor_plan_floor_4 INTEGER,
    floor_plan_rooms_4 INTEGER,
    floor_plan_type_5 floor_plan_type_enum,
    floor_plan_tatami_5 INTEGER,
    floor_plan_floor_5 INTEGER,
    floor_plan_rooms_5 INTEGER,
    floor_plan_type_6 floor_plan_type_enum,
    floor_plan_tatami_6 INTEGER,
    floor_plan_floor_6 INTEGER,
    floor_plan_rooms_6 INTEGER,
    floor_plan_type_7 floor_plan_type_enum,
    floor_plan_tatami_7 INTEGER,
    floor_plan_floor_7 INTEGER,
    floor_plan_rooms_7 INTEGER,
    floor_plan_type_8 floor_plan_type_enum,
    floor_plan_tatami_8 INTEGER,
    floor_plan_floor_8 INTEGER,
    floor_plan_rooms_8 INTEGER,
    floor_plan_type_9 floor_plan_type_enum,
    floor_plan_tatami_9 INTEGER,
    floor_plan_floor_9 INTEGER,
    floor_plan_rooms_9 INTEGER,
    floor_plan_type_10 floor_plan_type_enum,
    floor_plan_tatami_10 INTEGER,
    floor_plan_floor_10 INTEGER,
    floor_plan_rooms_10 INTEGER,
    floor_plan_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id)
);

-- 8. properties_contract（契約情報）- 23カラム
CREATE TABLE IF NOT EXISTS properties_contract (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    contract_period_years INTEGER,
    contract_period_months INTEGER,
    contract_period_type contract_period_type_enum,
    current_status current_status_enum,
    move_in_timing move_in_timing_enum,
    move_in_date DATE,
    move_in_period move_in_period_enum,
    property_manager_name VARCHAR(500),
    transaction_type VARCHAR(100),
    listing_confirmation_date VARCHAR(500),
    tenant_placement tenant_placement_enum,
    brokerage_contract_date DATE,
    brokerage_fee INTEGER,
    commission_split_ratio NUMERIC(10,2),
    contract_type contract_type_enum,
    property_publication_type property_publication_type_enum,
    contractor_company_name VARCHAR(200),
    contractor_contact_person VARCHAR(100),
    contractor_phone VARCHAR(20),
    contractor_email VARCHAR(200),
    contractor_address VARCHAR(500),
    contractor_license_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id)
);

-- 9. properties_roads（接道情報）- 16カラム
CREATE TABLE IF NOT EXISTS properties_roads (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    road_frontage_status road_frontage_status_enum,
    road_direction_1 road_direction_enum,
    road_frontage_width_1 INTEGER,
    road_type_1 road_type_enum,
    road_width_1 INTEGER,
    designated_road_1 designated_road_enum,
    road_direction_2 road_direction_enum,
    road_frontage_width_2 INTEGER,
    road_type_2 road_type_enum,
    road_width_2 INTEGER,
    designated_road_2 designated_road_enum,
    road_direction_3 road_direction_enum,
    road_frontage_width_3 INTEGER,
    road_type_3 road_type_enum,
    road_width_3 INTEGER,
    designated_road_3 designated_road_enum,
    road_direction_4 road_direction_enum,
    road_frontage_width_4 INTEGER,
    road_type_4 road_type_enum,
    road_width_4 INTEGER,
    designated_road_4 designated_road_enum,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id)
);

-- 10. properties_other（その他情報）- 40カラム
CREATE TABLE IF NOT EXISTS properties_other (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    land_category VARCHAR(100),
    use_district VARCHAR(100),
    city_planning VARCHAR(100),
    topography topography_enum,
    land_area_measurement land_area_measurement_enum,
    lot_area NUMERIC(10,2),
    private_road_area NUMERIC(10,2),
    private_road_ratio INTEGER,
    land_ownership_ratio INTEGER,
    setback setback_enum,
    setback_amount NUMERIC(10,2),
    building_coverage_ratio NUMERIC(10,2),
    floor_area_ratio NUMERIC(10,2),
    land_rights INTEGER,
    land_transaction_notice land_transaction_notice_enum,
    legal_restrictions VARCHAR(500),
    property_features TEXT,
    notes TEXT,
    url VARCHAR(500),
    internal_memo TEXT,
    affiliated_group VARCHAR(500),
    recommendation_points INTEGER,
    renovation_water VARCHAR(500),
    renovation_water_other VARCHAR(500),
    renovation_water_completion DATE,
    renovation_interior VARCHAR(500),
    renovation_interior_other VARCHAR(500),
    renovation_interior_completion DATE,
    renovation_exterior VARCHAR(500),
    renovation_exterior_other VARCHAR(500),
    renovation_exterior_completion DATE,
    renovation_common_area VARCHAR(500),
    renovation_common_completion DATE,
    renovation_notes TEXT,
    energy_consumption_min INTEGER,
    energy_consumption_max INTEGER,
    insulation_performance_min INTEGER,
    insulation_performance_max INTEGER,
    utility_cost_min INTEGER,
    utility_cost_max INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id)
);

-- 11. properties_facilities（周辺施設情報）- 18カラム
CREATE TABLE IF NOT EXISTS properties_facilities (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    elementary_school_name VARCHAR(500),
    elementary_school_distance INTEGER,
    junior_high_school_name VARCHAR(500),
    junior_high_school_distance INTEGER,
    convenience_store_distance INTEGER,
    supermarket_distance INTEGER,
    general_hospital_distance INTEGER,
    facilities_conditions VARCHAR(500),
    shopping_street_distance INTEGER,
    drugstore_distance INTEGER,
    park_distance INTEGER,
    bank_distance INTEGER,
    other_facility_name VARCHAR(500),
    other_facility_distance INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id)
);

-- ========================================
-- 4. マスターテーブル作成
-- ========================================

-- building_structure（建物構造マスター）
CREATE TABLE IF NOT EXISTS building_structure (
    id VARCHAR(20) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    group_name VARCHAR(100),
    homes_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- current_status（現況マスター）
CREATE TABLE IF NOT EXISTS current_status (
    id VARCHAR(30) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    group_name VARCHAR(100),
    homes_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- property_types（物件種別マスター）
CREATE TABLE IF NOT EXISTS property_types (
    id VARCHAR(40) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    group_name VARCHAR(100),
    homes_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- zoning_districts（用途地域マスター）
CREATE TABLE IF NOT EXISTS zoning_districts (
    id VARCHAR(40) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    group_name VARCHAR(100),
    homes_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- land_rights（土地権利マスター）
CREATE TABLE IF NOT EXISTS land_rights (
    id VARCHAR(30) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    group_name VARCHAR(100),
    homes_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- equipment_master（設備マスター）
CREATE TABLE IF NOT EXISTS equipment_master (
    id VARCHAR(50) PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    tab_group VARCHAR(100),
    display_name VARCHAR(100),
    data_type VARCHAR(50),
    dependent_items TEXT,
    remarks TEXT,
    homes_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- floor_plan_room_types（間取りタイプマスター）
CREATE TABLE IF NOT EXISTS floor_plan_room_types (
    id VARCHAR(20) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    group_name VARCHAR(100),
    homes_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- image_types（画像種別マスター）
CREATE TABLE IF NOT EXISTS image_types (
    id VARCHAR(30) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    group_name VARCHAR(100),
    homes_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- property_equipment（物件-設備の中間テーブル）
CREATE TABLE IF NOT EXISTS property_equipment (
    id BIGSERIAL PRIMARY KEY,
    property_id BIGINT NOT NULL,
    equipment_id VARCHAR(50) NOT NULL,
    value VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- column_labels（カラムメタデータ）
CREATE TABLE IF NOT EXISTS column_labels (
    table_name VARCHAR(100) NOT NULL,
    column_name VARCHAR(100) NOT NULL,
    japanese_label VARCHAR(200) NOT NULL,
    description TEXT,
    data_type VARCHAR(100),
    is_required BOOLEAN,
    display_order INTEGER,
    group_name VARCHAR(100),
    input_type VARCHAR(50),
    max_length INTEGER,
    enum_values TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (table_name, column_name)
);

-- ========================================
-- 5. インデックス作成
-- ========================================

-- properties_pricing
CREATE INDEX idx_properties_pricing_property_id ON properties_pricing(property_id);
CREATE INDEX idx_properties_pricing_price ON properties_pricing(price);
CREATE INDEX idx_properties_pricing_created_at ON properties_pricing(created_at);

-- properties_location
CREATE INDEX idx_properties_location_property_id ON properties_location(property_id);
CREATE INDEX idx_properties_location_postal_code ON properties_location(postal_code);
CREATE INDEX idx_properties_location_created_at ON properties_location(created_at);

-- properties_transportation
CREATE INDEX idx_properties_transportation_property_id ON properties_transportation(property_id);
CREATE INDEX idx_properties_transportation_created_at ON properties_transportation(created_at);

-- properties_images
CREATE INDEX idx_properties_images_property_id ON properties_images(property_id);
CREATE INDEX idx_properties_images_created_at ON properties_images(created_at);

-- properties_building
CREATE INDEX idx_properties_building_property_id ON properties_building(property_id);
CREATE INDEX idx_properties_building_created_at ON properties_building(created_at);

-- properties_floor_plans
CREATE INDEX idx_properties_floor_plans_property_id ON properties_floor_plans(property_id);
CREATE INDEX idx_properties_floor_plans_created_at ON properties_floor_plans(created_at);

-- properties_contract
CREATE INDEX idx_properties_contract_property_id ON properties_contract(property_id);
CREATE INDEX idx_properties_contract_created_at ON properties_contract(created_at);

-- properties_roads
CREATE INDEX idx_properties_roads_property_id ON properties_roads(property_id);
CREATE INDEX idx_properties_roads_created_at ON properties_roads(created_at);

-- properties_other
CREATE INDEX idx_properties_other_property_id ON properties_other(property_id);
CREATE INDEX idx_properties_other_created_at ON properties_other(created_at);

-- properties_facilities
CREATE INDEX idx_properties_facilities_property_id ON properties_facilities(property_id);
CREATE INDEX idx_properties_facilities_created_at ON properties_facilities(created_at);

-- ========================================
-- 6. トリガー関数
-- ========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 各テーブルにトリガーを設定
CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_pricing_updated_at BEFORE UPDATE ON properties_pricing
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_location_updated_at BEFORE UPDATE ON properties_location
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_transportation_updated_at BEFORE UPDATE ON properties_transportation
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_images_updated_at BEFORE UPDATE ON properties_images
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_building_updated_at BEFORE UPDATE ON properties_building
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_floor_plans_updated_at BEFORE UPDATE ON properties_floor_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_contract_updated_at BEFORE UPDATE ON properties_contract
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_roads_updated_at BEFORE UPDATE ON properties_roads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_other_updated_at BEFORE UPDATE ON properties_other
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_facilities_updated_at BEFORE UPDATE ON properties_facilities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_column_labels_updated_at BEFORE UPDATE ON column_labels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 7. マスターデータ投入
-- ========================================

-- building_structure（建物構造マスター）- 12件
INSERT INTO building_structure (id, label, group_name) VALUES
('wood', '木造', '木造系'),
('steel', '鉄骨造', '鉄骨系'),
('rc', 'RC造', 'コンクリート系'),
('src', 'SRC造', 'コンクリート系'),
('pc', 'PC造', 'コンクリート系'),
('hpc', 'HPC造', 'コンクリート系'),
('lgs', '軽量鉄骨造', '鉄骨系'),
('cbb', 'コンクリートブロック造', 'コンクリート系'),
('alc', 'ALC造', 'その他'),
('pcpanel', 'PCパネル造', 'コンクリート系'),
('log', 'ログハウス', '木造系'),
('other', 'その他', 'その他');

-- current_status（現況マスター）- 9件
INSERT INTO current_status (id, label) VALUES
('vacant', '空室'),
('vacant_scheduled', '空予定'),
('rented', '賃貸中'),
('occupied', '居住中'),
('office_use', '事務所使用'),
('under_construction', '建築中'),
('completed', '完成済'),
('undecided', '未定'),
('other', 'その他');

-- property_types（物件種別マスター）- 主要なもののみ
INSERT INTO property_types (id, label, group_name) VALUES
('apartment', 'アパート', '居住用'),
('mansion', 'マンション', '居住用'),
('detached', '一戸建て', '居住用'),
('terrace', 'テラスハウス', '居住用'),
('townhouse', 'タウンハウス', '居住用'),
('store', '店舗', '事業用'),
('office', '事務所', '事業用'),
('warehouse', '倉庫', '事業用'),
('factory', '工場', '事業用'),
('parking', '駐車場', 'その他'),
('land', '土地', 'その他'),
('building', '一棟売りビル', '投資用'),
('apartment_building', '一棟売りアパート', '投資用'),
('mansion_building', '一棟売りマンション', '投資用');

-- zoning_districts（用途地域マスター）- 14件
INSERT INTO zoning_districts (id, label, group_name) VALUES
('1st_low_res', '第一種低層住居専用地域', '住居系'),
('2nd_low_res', '第二種低層住居専用地域', '住居系'),
('1st_mid_res', '第一種中高層住居専用地域', '住居系'),
('2nd_mid_res', '第二種中高層住居専用地域', '住居系'),
('1st_res', '第一種住居地域', '住居系'),
('2nd_res', '第二種住居地域', '住居系'),
('quasi_res', '準住居地域', '住居系'),
('neighbor_com', '近隣商業地域', '商業系'),
('commercial', '商業地域', '商業系'),
('quasi_ind', '準工業地域', '工業系'),
('industrial', '工業地域', '工業系'),
('excl_ind', '工業専用地域', '工業系'),
('undesignated', '指定なし', 'その他'),
('urbanization_control', '市街化調整区域', 'その他');

-- land_rights（土地権利マスター）- 12件
INSERT INTO land_rights (id, label, group_name) VALUES
('ownership', '所有権', '所有権'),
('leasehold', '借地権', '借地権'),
('fixed_leasehold', '定期借地権', '借地権'),
('general_fixed', '一般定期借地権', '借地権'),
('business_fixed', '事業用定期借地権', '借地権'),
('building_transfer', '建物譲渡特約付借地権', '借地権'),
('old_leasehold', '旧法借地権', '借地権'),
('surface', '地上権', 'その他'),
('rental', '賃借権', 'その他'),
('usage', '使用貸借権', 'その他'),
('sectional', '区分地上権', 'その他'),
('other', 'その他', 'その他');

-- floor_plan_room_types（間取りタイプマスター）- 9件
INSERT INTO floor_plan_room_types (id, label) VALUES
('r', 'R'),
('k', 'K'),
('dk', 'DK'),
('ldk', 'LDK'),
('sldk', 'SLDK'),
('l', 'L'),
('d', 'D'),
('s', 'S'),
('other', 'その他');

-- image_types（画像種別マスター）- 22件
INSERT INTO image_types (id, label, group_name) VALUES
('exterior', '外観', '建物外部'),
('floorplan', '間取図', '図面'),
('room', '居室', '室内'),
('kitchen', 'キッチン', '室内'),
('bath', '風呂', '室内'),
('toilet', 'トイレ', '室内'),
('washroom', '洗面', '室内'),
('equipment', '設備', '室内'),
('entrance', '玄関', '室内'),
('balcony', 'バルコニー', '建物外部'),
('view', '眺望', 'その他'),
('common', '共用部', '建物共用'),
('surrounding', '周辺環境', '周辺'),
('parking', '駐車場', '建物外部'),
('garden', '庭', '建物外部'),
('living', 'リビング', '室内'),
('bedroom', '寝室', '室内'),
('closet', '収納', '室内'),
('hallway', '廊下', '室内'),
('aerial', '航空写真', 'その他'),
('map', '地図', 'その他'),
('other', 'その他', 'その他');

-- equipment_master（設備マスター）- 一部のみ
INSERT INTO equipment_master (id, item_name, tab_group, display_name) VALUES
-- 建物設備
('elevator', 'エレベーター', '建物設備', 'エレベーター'),
('auto_lock', 'オートロック', '建物設備', 'オートロック'),
('delivery_box', '宅配ボックス', '建物設備', '宅配ボックス'),
('trash_24h', '24時間ゴミ出し可', '建物設備', '24時間ゴミ出し可'),
('bike_parking', '駐輪場', '建物設備', '駐輪場'),
('motorcycle_parking', 'バイク置場', '建物設備', 'バイク置場'),
-- 室内設備
('system_kitchen', 'システムキッチン', '室内設備', 'システムキッチン'),
('gas_stove', 'ガスコンロ', '室内設備', 'ガスコンロ'),
('ih_stove', 'IHコンロ', '室内設備', 'IHコンロ'),
('bathroom_dryer', '浴室乾燥機', '室内設備', '浴室乾燥機'),
('reheating_bath', '追焚機能', '室内設備', '追焚機能'),
('washlet', '温水洗浄便座', '室内設備', '温水洗浄便座'),
('air_conditioner', 'エアコン', '室内設備', 'エアコン'),
('floor_heating', '床暖房', '室内設備', '床暖房');

-- ========================================
-- 8. 外部キー制約の追加
-- ========================================

-- property_equipment の外部キー
ALTER TABLE property_equipment 
ADD CONSTRAINT fk_property_equipment_property 
FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE;

ALTER TABLE property_equipment 
ADD CONSTRAINT fk_property_equipment_equipment 
FOREIGN KEY (equipment_id) REFERENCES equipment_master(id);

-- propertiesテーブルの外部キー（マスターテーブルへの参照）
ALTER TABLE properties
ADD CONSTRAINT fk_properties_building_structure
FOREIGN KEY (building_structure_id) REFERENCES building_structure(id);

ALTER TABLE properties
ADD CONSTRAINT fk_properties_current_status
FOREIGN KEY (current_status_id) REFERENCES current_status(id);

ALTER TABLE properties
ADD CONSTRAINT fk_properties_property_type
FOREIGN KEY (property_type_id) REFERENCES property_types(id);

ALTER TABLE properties
ADD CONSTRAINT fk_properties_zoning_district
FOREIGN KEY (zoning_district_id) REFERENCES zoning_districts(id);

ALTER TABLE properties
ADD CONSTRAINT fk_properties_land_rights
FOREIGN KEY (land_rights_id) REFERENCES land_rights(id);

-- ========================================
-- 9. 完了メッセージ
-- ========================================

DO $$
BEGIN
    RAISE NOTICE '✅ REAデータベース復旧完了！';
    RAISE NOTICE '📊 作成されたテーブル:';
    RAISE NOTICE '  - 基本情報: properties';
    RAISE NOTICE '  - 価格情報: properties_pricing (16カラム)';
    RAISE NOTICE '  - 所在地: properties_location (11カラム), properties_transportation (15カラム)';
    RAISE NOTICE '  - 画像: properties_images (94カラム)';
    RAISE NOTICE '  - 建物: properties_building (37カラム), properties_floor_plans (45カラム)';
    RAISE NOTICE '  - 契約: properties_contract (23カラム)';
    RAISE NOTICE '  - 土地: properties_roads (16カラム), properties_other (40カラム)';
    RAISE NOTICE '  - 施設: properties_facilities (18カラム)';
    RAISE NOTICE '  - マスター: 8テーブル';
    RAISE NOTICE '  - その他: property_equipment, column_labels';
    RAISE NOTICE '🎉 合計26テーブル分割構造復旧完了！';
END $$;