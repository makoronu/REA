-- REA Database Split: New Tables Creation
-- Generated: 2025-07-21 15:30:18
-- PostgreSQL Admin実行用

BEGIN;

-- 📍 所在地・交通テーブル
CREATE TABLE IF NOT EXISTS properties_location (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    postal_code character varying, -- location関連のpostal_code
    address_code integer, -- location関連のaddress_code
    address_name character varying, -- 住所名
    address_detail_public text, -- location関連のaddress_detail_public
    address_detail_private text, -- location関連のaddress_detail_private
    latitude_longitude character varying, -- location関連のlatitude_longitude
    train_line_1 character varying, -- 最寄り路線1
    station_1 character varying, -- location関連のstation_1
    bus_stop_name_1 character varying, -- location関連のbus_stop_name_1
    bus_time_1 integer, -- location関連のbus_time_1
    walking_distance_1 integer, -- location関連のwalking_distance_1
    train_line_2 character varying, -- location関連のtrain_line_2
    station_2 character varying, -- location関連のstation_2
    bus_stop_name_2 character varying, -- location関連のbus_stop_name_2
    bus_time_2 integer, -- location関連のbus_time_2
    walking_distance_2 integer, -- location関連のwalking_distance_2
    contractor_address character varying, -- location関連のcontractor_address
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

COMMENT ON TABLE properties_location IS '住所・路線・駅・徒歩時間情報';

-- 📝 その他情報テーブル
CREATE TABLE IF NOT EXISTS properties_other (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    other_transportation character varying, -- other関連のother_transportation
    land_category character varying, -- other関連のland_category
    use_district character varying, -- other関連のuse_district
    city_planning character varying, -- other関連のcity_planning
    topography USER-DEFINED, -- other関連のtopography
    private_road_ratio integer, -- other関連のprivate_road_ratio
    land_ownership_ratio integer, -- other関連のland_ownership_ratio
    setback USER-DEFINED, -- other関連のsetback
    setback_amount numeric, -- other関連のsetback_amount
    road_direction_1 USER-DEFINED, -- other関連のroad_direction_1
    road_type_1 USER-DEFINED, -- other関連のroad_type_1
    designated_road_1 USER-DEFINED, -- other関連のdesignated_road_1
    road_direction_2 USER-DEFINED, -- other関連のroad_direction_2
    road_type_2 USER-DEFINED, -- other関連のroad_type_2
    designated_road_2 USER-DEFINED, -- other関連のdesignated_road_2
    road_direction_3 USER-DEFINED, -- other関連のroad_direction_3
    road_type_3 USER-DEFINED, -- other関連のroad_type_3
    designated_road_3 USER-DEFINED, -- other関連のdesignated_road_3
    road_direction_4 USER-DEFINED, -- other関連のroad_direction_4
    road_type_4 USER-DEFINED, -- other関連のroad_type_4
    designated_road_4 USER-DEFINED, -- other関連のdesignated_road_4
    land_rights integer, -- other関連のland_rights
    land_transaction_notice USER-DEFINED, -- other関連のland_transaction_notice
    legal_restrictions character varying, -- other関連のlegal_restrictions
    management_type character varying, -- other関連のmanagement_type
    management_association USER-DEFINED, -- other関連のmanagement_association
    management_company character varying, -- other関連のmanagement_company
    direction USER-DEFINED, -- other関連のdirection
    room_count integer, -- other関連のroom_count
    room_type USER-DEFINED, -- other関連のroom_type
    property_features text, -- other関連のproperty_features
    notes text, -- other関連のnotes
    url character varying, -- other関連のurl
    internal_memo text, -- other関連のinternal_memo
    parking_type USER-DEFINED, -- other関連のparking_type
    parking_available integer, -- other関連のparking_available
    parking_notes text, -- other関連のparking_notes
    move_in_timing USER-DEFINED, -- other関連のmove_in_timing
    move_in_date date, -- other関連のmove_in_date
    move_in_period USER-DEFINED, -- other関連のmove_in_period
    elementary_school_name character varying, -- other関連のelementary_school_name
    junior_high_school_name character varying, -- other関連のjunior_high_school_name
    property_manager_name character varying, -- other関連のproperty_manager_name
    transaction_type character varying, -- other関連のtransaction_type
    listing_confirmation_date character varying, -- other関連のlisting_confirmation_date
    tenant_placement USER-DEFINED, -- other関連のtenant_placement
    commission_split_ratio numeric, -- other関連のcommission_split_ratio
    affiliated_group character varying, -- other関連のaffiliated_group
    facilities_conditions character varying, -- other関連のfacilities_conditions
    recommendation_points integer, -- other関連のrecommendation_points
    move_in_consultation USER-DEFINED, -- other関連のmove_in_consultation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

COMMENT ON TABLE properties_other IS '分類できないその他の情報';

-- 🏗️ 建物情報テーブル
CREATE TABLE IF NOT EXISTS properties_building (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    land_area_measurement USER-DEFINED, -- building関連のland_area_measurement
    lot_area numeric, -- building関連のlot_area
    private_road_area numeric, -- building関連のprivate_road_area
    building_coverage_ratio numeric, -- building関連のbuilding_coverage_ratio
    floor_area_ratio numeric, -- building関連のfloor_area_ratio
    building_structure character varying, -- building関連のbuilding_structure
    building_area_measurement USER-DEFINED, -- building関連のbuilding_area_measurement
    building_exclusive_area numeric, -- building関連のbuilding_exclusive_area
    total_site_area numeric, -- building関連のtotal_site_area
    total_floor_area numeric, -- building関連のtotal_floor_area
    building_area numeric, -- building関連のbuilding_area
    building_floors_above integer, -- building関連のbuilding_floors_above
    building_floors_below integer, -- building関連のbuilding_floors_below
    construction_date date, -- building関連のconstruction_date
    building_manager USER-DEFINED, -- building関連のbuilding_manager
    room_floor integer, -- building関連のroom_floor
    balcony_area numeric, -- building関連のbalcony_area
    floor_plan_type_1 USER-DEFINED, -- building関連のfloor_plan_type_1
    floor_plan_tatami_1 integer, -- building関連のfloor_plan_tatami_1
    floor_plan_floor_1 integer, -- building関連のfloor_plan_floor_1
    floor_plan_rooms_1 integer, -- building関連のfloor_plan_rooms_1
    floor_plan_type_2 USER-DEFINED, -- building関連のfloor_plan_type_2
    floor_plan_tatami_2 integer, -- building関連のfloor_plan_tatami_2
    floor_plan_floor_2 integer, -- building関連のfloor_plan_floor_2
    floor_plan_rooms_2 integer, -- building関連のfloor_plan_rooms_2
    floor_plan_type_3 USER-DEFINED, -- building関連のfloor_plan_type_3
    floor_plan_tatami_3 integer, -- building関連のfloor_plan_tatami_3
    floor_plan_floor_3 integer, -- building関連のfloor_plan_floor_3
    floor_plan_rooms_3 integer, -- building関連のfloor_plan_rooms_3
    floor_plan_type_4 USER-DEFINED, -- building関連のfloor_plan_type_4
    floor_plan_tatami_4 integer, -- building関連のfloor_plan_tatami_4
    floor_plan_floor_4 integer, -- building関連のfloor_plan_floor_4
    floor_plan_rooms_4 integer, -- building関連のfloor_plan_rooms_4
    floor_plan_type_5 USER-DEFINED, -- building関連のfloor_plan_type_5
    floor_plan_tatami_5 integer, -- building関連のfloor_plan_tatami_5
    floor_plan_floor_5 integer, -- building関連のfloor_plan_floor_5
    floor_plan_rooms_5 integer, -- building関連のfloor_plan_rooms_5
    floor_plan_type_6 USER-DEFINED, -- building関連のfloor_plan_type_6
    floor_plan_tatami_6 integer, -- building関連のfloor_plan_tatami_6
    floor_plan_floor_6 integer, -- building関連のfloor_plan_floor_6
    floor_plan_rooms_6 integer, -- building関連のfloor_plan_rooms_6
    floor_plan_type_7 USER-DEFINED, -- building関連のfloor_plan_type_7
    floor_plan_tatami_7 integer, -- building関連のfloor_plan_tatami_7
    floor_plan_floor_7 integer, -- building関連のfloor_plan_floor_7
    floor_plan_rooms_7 integer, -- building関連のfloor_plan_rooms_7
    floor_plan_type_8 USER-DEFINED, -- building関連のfloor_plan_type_8
    floor_plan_tatami_8 integer, -- building関連のfloor_plan_tatami_8
    floor_plan_floor_8 integer, -- building関連のfloor_plan_floor_8
    floor_plan_rooms_8 integer, -- building関連のfloor_plan_rooms_8
    floor_plan_type_9 USER-DEFINED, -- building関連のfloor_plan_type_9
    floor_plan_tatami_9 integer, -- building関連のfloor_plan_tatami_9
    floor_plan_floor_9 integer, -- building関連のfloor_plan_floor_9
    floor_plan_rooms_9 integer, -- building関連のfloor_plan_rooms_9
    floor_plan_type_10 USER-DEFINED, -- building関連のfloor_plan_type_10
    floor_plan_tatami_10 integer, -- building関連のfloor_plan_tatami_10
    floor_plan_floor_10 integer, -- building関連のfloor_plan_floor_10
    floor_plan_rooms_10 integer, -- building関連のfloor_plan_rooms_10
    floor_plan_notes text, -- building関連のfloor_plan_notes
    renovation_common_area character varying, -- building関連のrenovation_common_area
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

COMMENT ON TABLE properties_building IS '建物構造・築年数・間取り・面積情報';

-- 💰 価格・収益テーブル
CREATE TABLE IF NOT EXISTS properties_pricing (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    rent_price integer, -- 賃料（円）
    tax USER-DEFINED, -- pricing関連のtax
    tax_amount USER-DEFINED, -- pricing関連のtax_amount
    price_per_tsubo integer, -- pricing関連のprice_per_tsubo
    common_management_fee integer, -- pricing関連のcommon_management_fee
    common_management_fee_tax USER-DEFINED, -- pricing関連のcommon_management_fee_tax
    full_occupancy_yield integer, -- pricing関連のfull_occupancy_yield
    current_yield integer, -- pricing関連のcurrent_yield
    housing_insurance integer, -- pricing関連のhousing_insurance
    land_rent integer, -- pricing関連のland_rent
    contract_period_years integer, -- pricing関連のcontract_period_years
    contract_period_months integer, -- pricing関連のcontract_period_months
    contract_period_type USER-DEFINED, -- pricing関連のcontract_period_type
    repair_reserve_fund integer, -- pricing関連のrepair_reserve_fund
    repair_reserve_fund_base integer, -- pricing関連のrepair_reserve_fund_base
    parking_fee integer, -- pricing関連のparking_fee
    parking_fee_tax USER-DEFINED, -- pricing関連のparking_fee_tax
    brokerage_fee integer, -- pricing関連のbrokerage_fee
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

COMMENT ON TABLE properties_pricing IS '賃料・価格・収益・費用関連情報';

-- 🏫 周辺施設テーブル
CREATE TABLE IF NOT EXISTS properties_facilities (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    parking_distance integer, -- facilities関連のparking_distance
    elementary_school_distance integer, -- facilities関連のelementary_school_distance
    junior_high_school_distance integer, -- facilities関連のjunior_high_school_distance
    convenience_store_distance integer, -- facilities関連のconvenience_store_distance
    supermarket_distance integer, -- facilities関連のsupermarket_distance
    general_hospital_distance integer, -- facilities関連のgeneral_hospital_distance
    shopping_street_distance integer, -- facilities関連のshopping_street_distance
    drugstore_distance integer, -- facilities関連のdrugstore_distance
    park_distance integer, -- facilities関連のpark_distance
    bank_distance integer, -- facilities関連のbank_distance
    other_facility_name character varying, -- facilities関連のother_facility_name
    other_facility_distance integer, -- facilities関連のother_facility_distance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

COMMENT ON TABLE properties_facilities IS '周辺環境・施設・距離情報';

-- 📋 契約情報テーブル
CREATE TABLE IF NOT EXISTS properties_contract (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    brokerage_contract_date date, -- contract関連のbrokerage_contract_date
    contract_type USER-DEFINED, -- contract関連のcontract_type
    property_publication_type USER-DEFINED, -- contract関連のproperty_publication_type
    contractor_company_name character varying, -- contract関連のcontractor_company_name
    contractor_contact_person character varying, -- contract関連のcontractor_contact_person
    contractor_phone character varying, -- contract関連のcontractor_phone
    contractor_email character varying, -- contract関連のcontractor_email
    contractor_license_number character varying, -- contract関連のcontractor_license_number
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

COMMENT ON TABLE properties_contract IS '契約条件・業者情報';

-- 📸 画像管理テーブル
CREATE TABLE IF NOT EXISTS properties_images (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    image_type_1 USER-DEFINED, -- 画像種別1
    image_comment_1 text, -- images関連のimage_comment_1
    local_file_name_2 character varying, -- images関連のlocal_file_name_2
    image_type_2 USER-DEFINED, -- images関連のimage_type_2
    image_comment_2 text, -- images関連のimage_comment_2
    local_file_name_3 character varying, -- images関連のlocal_file_name_3
    image_type_3 USER-DEFINED, -- images関連のimage_type_3
    image_comment_3 text, -- images関連のimage_comment_3
    local_file_name_4 character varying, -- images関連のlocal_file_name_4
    image_type_4 USER-DEFINED, -- images関連のimage_type_4
    image_comment_4 text, -- images関連のimage_comment_4
    local_file_name_5 character varying, -- images関連のlocal_file_name_5
    image_type_5 USER-DEFINED, -- images関連のimage_type_5
    image_comment_5 text, -- images関連のimage_comment_5
    local_file_name_6 character varying, -- images関連のlocal_file_name_6
    image_type_6 USER-DEFINED, -- images関連のimage_type_6
    image_comment_6 text, -- images関連のimage_comment_6
    image_type_7 USER-DEFINED, -- images関連のimage_type_7
    image_comment_7 text, -- images関連のimage_comment_7
    local_file_name_8 character varying, -- images関連のlocal_file_name_8
    image_type_8 USER-DEFINED, -- images関連のimage_type_8
    image_comment_8 text, -- images関連のimage_comment_8
    local_file_name_9 character varying, -- images関連のlocal_file_name_9
    image_type_9 USER-DEFINED, -- images関連のimage_type_9
    image_comment_9 text, -- images関連のimage_comment_9
    local_file_name_10 character varying, -- images関連のlocal_file_name_10
    image_type_10 USER-DEFINED, -- images関連のimage_type_10
    image_comment_10 text, -- images関連のimage_comment_10
    local_file_name_11 character varying, -- images関連のlocal_file_name_11
    image_type_11 USER-DEFINED, -- images関連のimage_type_11
    image_comment_11 text, -- images関連のimage_comment_11
    local_file_name_12 character varying, -- images関連のlocal_file_name_12
    image_type_12 USER-DEFINED, -- images関連のimage_type_12
    image_comment_12 text, -- images関連のimage_comment_12
    local_file_name_13 character varying, -- images関連のlocal_file_name_13
    image_type_13 USER-DEFINED, -- images関連のimage_type_13
    image_comment_13 text, -- images関連のimage_comment_13
    local_file_name_14 character varying, -- images関連のlocal_file_name_14
    image_type_14 USER-DEFINED, -- images関連のimage_type_14
    image_comment_14 text, -- images関連のimage_comment_14
    local_file_name_15 character varying, -- images関連のlocal_file_name_15
    image_type_15 USER-DEFINED, -- images関連のimage_type_15
    image_comment_15 text, -- images関連のimage_comment_15
    local_file_name_16 character varying, -- images関連のlocal_file_name_16
    image_type_16 USER-DEFINED, -- images関連のimage_type_16
    image_comment_16 text, -- images関連のimage_comment_16
    local_file_name_17 character varying, -- images関連のlocal_file_name_17
    image_type_17 USER-DEFINED, -- images関連のimage_type_17
    image_comment_17 text, -- images関連のimage_comment_17
    local_file_name_18 character varying, -- images関連のlocal_file_name_18
    image_type_18 USER-DEFINED, -- images関連のimage_type_18
    image_comment_18 text, -- images関連のimage_comment_18
    local_file_name_19 character varying, -- images関連のlocal_file_name_19
    image_type_19 USER-DEFINED, -- images関連のimage_type_19
    image_comment_19 text, -- images関連のimage_comment_19
    local_file_name_20 character varying, -- images関連のlocal_file_name_20
    image_type_20 USER-DEFINED, -- images関連のimage_type_20
    image_comment_20 text, -- images関連のimage_comment_20
    local_file_name_21 character varying, -- images関連のlocal_file_name_21
    image_type_21 USER-DEFINED, -- images関連のimage_type_21
    image_comment_21 text, -- images関連のimage_comment_21
    local_file_name_22 character varying, -- images関連のlocal_file_name_22
    image_type_22 USER-DEFINED, -- images関連のimage_type_22
    image_comment_22 text, -- images関連のimage_comment_22
    local_file_name_23 character varying, -- images関連のlocal_file_name_23
    image_type_23 USER-DEFINED, -- images関連のimage_type_23
    image_comment_23 text, -- images関連のimage_comment_23
    local_file_name_24 character varying, -- images関連のlocal_file_name_24
    image_type_24 USER-DEFINED, -- images関連のimage_type_24
    image_comment_24 text, -- images関連のimage_comment_24
    local_file_name_25 character varying, -- images関連のlocal_file_name_25
    image_type_25 USER-DEFINED, -- images関連のimage_type_25
    image_comment_25 text, -- images関連のimage_comment_25
    local_file_name_26 character varying, -- images関連のlocal_file_name_26
    image_type_26 USER-DEFINED, -- images関連のimage_type_26
    image_comment_26 text, -- images関連のimage_comment_26
    local_file_name_27 character varying, -- images関連のlocal_file_name_27
    image_type_27 USER-DEFINED, -- images関連のimage_type_27
    image_comment_27 text, -- images関連のimage_comment_27
    local_file_name_28 character varying, -- images関連のlocal_file_name_28
    image_type_28 USER-DEFINED, -- images関連のimage_type_28
    image_comment_28 text, -- images関連のimage_comment_28
    local_file_name_29 character varying, -- images関連のlocal_file_name_29
    image_type_29 USER-DEFINED, -- images関連のimage_type_29
    image_comment_29 text, -- images関連のimage_comment_29
    local_file_name_30 character varying, -- images関連のlocal_file_name_30
    image_type_30 USER-DEFINED, -- images関連のimage_type_30
    image_comment_30 text, -- images関連のimage_comment_30
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

COMMENT ON TABLE properties_images IS '物件画像30セットの管理（90カラム→正規化）';

-- 🔧 リノベーション情報テーブル
CREATE TABLE IF NOT EXISTS properties_renovation (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    renovation_water character varying, -- renovation関連のrenovation_water
    renovation_water_other character varying, -- renovation関連のrenovation_water_other
    renovation_water_completion date, -- renovation関連のrenovation_water_completion
    renovation_interior character varying, -- renovation関連のrenovation_interior
    renovation_interior_other character varying, -- renovation関連のrenovation_interior_other
    renovation_interior_completion date, -- renovation関連のrenovation_interior_completion
    renovation_exterior character varying, -- renovation関連のrenovation_exterior
    renovation_exterior_other character varying, -- renovation関連のrenovation_exterior_other
    renovation_exterior_completion date, -- renovation関連のrenovation_exterior_completion
    renovation_common_completion date, -- renovation関連のrenovation_common_completion
    renovation_notes text, -- renovation関連のrenovation_notes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

COMMENT ON TABLE properties_renovation IS 'リノベーション履歴・予定情報';

-- ⚡ エネルギー性能テーブル
CREATE TABLE IF NOT EXISTS properties_energy (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL,
    energy_consumption_min integer, -- energy関連のenergy_consumption_min
    energy_consumption_max integer, -- energy関連のenergy_consumption_max
    insulation_performance_min integer, -- energy関連のinsulation_performance_min
    insulation_performance_max integer, -- energy関連のinsulation_performance_max
    utility_cost_min integer, -- energy関連のutility_cost_min
    utility_cost_max integer, -- energy関連のutility_cost_max
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

COMMENT ON TABLE properties_energy IS 'エネルギー消費・断熱性能・光熱費情報';

COMMIT;
