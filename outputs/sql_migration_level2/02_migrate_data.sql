-- REA Database Split Level 2: Data Migration
-- Generated: 2025-07-21 16:02:13
-- 将来データが追加された時用の移行SQL

BEGIN;

-- 🏗️ properties_buildingへのデータ移行
INSERT INTO properties_building (property_id, total_units, vacant_units, vacant_units_detail, lot_area, private_road_area, building_coverage_ratio, building_structure, building_area_measurement, building_exclusive_area, total_site_area, total_floor_area, building_area, building_floors_above, building_floors_below, construction_date, building_manager, management_type, management_association, management_company, room_floor, balcony_area, direction, room_count, room_type, common_management_fee, common_management_fee_tax, parking_fee, parking_fee_tax, parking_type, parking_distance, parking_available, parking_notes, renovation_common_area)
SELECT id, total_units, vacant_units, vacant_units_detail, lot_area, private_road_area, building_coverage_ratio, building_structure, building_area_measurement, building_exclusive_area, total_site_area, total_floor_area, building_area, building_floors_above, building_floors_below, construction_date, building_manager, management_type, management_association, management_company, room_floor, balcony_area, direction, room_count, room_type, common_management_fee, common_management_fee_tax, parking_fee, parking_fee_tax, parking_type, parking_distance, parking_available, parking_notes, renovation_common_area
FROM properties
WHERE id IS NOT NULL;

-- 📍 properties_locationへのデータ移行
INSERT INTO properties_location (property_id, postal_code, address_code, address_name, address_detail_public, address_detail_private, latitude_longitude, contractor_address)
SELECT id, postal_code, address_code, address_name, address_detail_public, address_detail_private, latitude_longitude, contractor_address
FROM properties
WHERE id IS NOT NULL;

-- 🚃 properties_transportationへのデータ移行
INSERT INTO properties_transportation (property_id, train_line_1, station_1, bus_stop_name_1, bus_time_1, walking_distance_1, train_line_2, station_2, bus_stop_name_2, bus_time_2, walking_distance_2, other_transportation)
SELECT id, train_line_1, station_1, bus_stop_name_1, bus_time_1, walking_distance_1, train_line_2, station_2, bus_stop_name_2, bus_time_2, walking_distance_2, other_transportation
FROM properties
WHERE id IS NOT NULL;

-- 📝 properties_otherへのデータ移行
INSERT INTO properties_other (property_id, land_category, use_district, city_planning, topography, land_area_measurement, private_road_ratio, land_ownership_ratio, setback, setback_amount, floor_area_ratio, land_rights, land_transaction_notice, legal_restrictions, property_features, notes, url, internal_memo, affiliated_group, recommendation_points, renovation_water, renovation_water_other, renovation_water_completion, renovation_interior, renovation_interior_other, renovation_interior_completion, renovation_exterior, renovation_exterior_other, renovation_exterior_completion, renovation_common_completion, renovation_notes, energy_consumption_min, energy_consumption_max, insulation_performance_min, insulation_performance_max, utility_cost_min, utility_cost_max)
SELECT id, land_category, use_district, city_planning, topography, land_area_measurement, private_road_ratio, land_ownership_ratio, setback, setback_amount, floor_area_ratio, land_rights, land_transaction_notice, legal_restrictions, property_features, notes, url, internal_memo, affiliated_group, recommendation_points, renovation_water, renovation_water_other, renovation_water_completion, renovation_interior, renovation_interior_other, renovation_interior_completion, renovation_exterior, renovation_exterior_other, renovation_exterior_completion, renovation_common_completion, renovation_notes, energy_consumption_min, energy_consumption_max, insulation_performance_min, insulation_performance_max, utility_cost_min, utility_cost_max
FROM properties
WHERE id IS NOT NULL;

-- 🛣️ properties_roadsへのデータ移行
INSERT INTO properties_roads (property_id, road_direction_1, road_type_1, designated_road_1, road_direction_2, road_type_2, designated_road_2, road_direction_3, road_type_3, designated_road_3, road_direction_4, road_type_4, designated_road_4)
SELECT id, road_direction_1, road_type_1, designated_road_1, road_direction_2, road_type_2, designated_road_2, road_direction_3, road_type_3, designated_road_3, road_direction_4, road_type_4, designated_road_4
FROM properties
WHERE id IS NOT NULL;

-- 🏠 properties_floor_plansへのデータ移行
INSERT INTO properties_floor_plans (property_id, floor_plan_type_1, floor_plan_tatami_1, floor_plan_floor_1, floor_plan_rooms_1, floor_plan_type_2, floor_plan_tatami_2, floor_plan_floor_2, floor_plan_rooms_2, floor_plan_type_3, floor_plan_tatami_3, floor_plan_floor_3, floor_plan_rooms_3, floor_plan_type_4, floor_plan_tatami_4, floor_plan_floor_4, floor_plan_rooms_4, floor_plan_type_5, floor_plan_tatami_5, floor_plan_floor_5, floor_plan_rooms_5, floor_plan_type_6, floor_plan_tatami_6, floor_plan_floor_6, floor_plan_rooms_6, floor_plan_type_7, floor_plan_tatami_7, floor_plan_floor_7, floor_plan_rooms_7, floor_plan_type_8, floor_plan_tatami_8, floor_plan_floor_8, floor_plan_rooms_8, floor_plan_type_9, floor_plan_tatami_9, floor_plan_floor_9, floor_plan_rooms_9, floor_plan_type_10, floor_plan_tatami_10, floor_plan_floor_10, floor_plan_rooms_10, floor_plan_notes)
SELECT id, floor_plan_type_1, floor_plan_tatami_1, floor_plan_floor_1, floor_plan_rooms_1, floor_plan_type_2, floor_plan_tatami_2, floor_plan_floor_2, floor_plan_rooms_2, floor_plan_type_3, floor_plan_tatami_3, floor_plan_floor_3, floor_plan_rooms_3, floor_plan_type_4, floor_plan_tatami_4, floor_plan_floor_4, floor_plan_rooms_4, floor_plan_type_5, floor_plan_tatami_5, floor_plan_floor_5, floor_plan_rooms_5, floor_plan_type_6, floor_plan_tatami_6, floor_plan_floor_6, floor_plan_rooms_6, floor_plan_type_7, floor_plan_tatami_7, floor_plan_floor_7, floor_plan_rooms_7, floor_plan_type_8, floor_plan_tatami_8, floor_plan_floor_8, floor_plan_rooms_8, floor_plan_type_9, floor_plan_tatami_9, floor_plan_floor_9, floor_plan_rooms_9, floor_plan_type_10, floor_plan_tatami_10, floor_plan_floor_10, floor_plan_rooms_10, floor_plan_notes
FROM properties
WHERE id IS NOT NULL;

-- 💰 properties_pricingへのデータ移行
INSERT INTO properties_pricing (property_id, price, tax, tax_amount, price_per_tsubo, full_occupancy_yield, current_yield, housing_insurance, land_rent, repair_reserve_fund, repair_reserve_fund_base, brokerage_fee, commission_split_ratio)
SELECT id, rent_price, tax, tax_amount, price_per_tsubo, full_occupancy_yield, current_yield, housing_insurance, land_rent, repair_reserve_fund, repair_reserve_fund_base, brokerage_fee, commission_split_ratio
FROM properties
WHERE id IS NOT NULL;

-- 📋 properties_contractへのデータ移行
INSERT INTO properties_contract (property_id, contract_period_years, contract_period_months, contract_period_type, move_in_timing, move_in_date, move_in_period, property_manager_name, transaction_type, listing_confirmation_date, tenant_placement, brokerage_contract_date, move_in_consultation, contract_type, property_publication_type, contractor_company_name, contractor_contact_person, contractor_phone, contractor_email, contractor_license_number)
SELECT id, contract_period_years, contract_period_months, contract_period_type, move_in_timing, move_in_date, move_in_period, property_manager_name, transaction_type, listing_confirmation_date, tenant_placement, brokerage_contract_date, move_in_consultation, contract_type, property_publication_type, contractor_company_name, contractor_contact_person, contractor_phone, contractor_email, contractor_license_number
FROM properties
WHERE id IS NOT NULL;

-- 🏫 properties_facilitiesへのデータ移行
INSERT INTO properties_facilities (property_id, elementary_school_name, elementary_school_distance, junior_high_school_name, junior_high_school_distance, convenience_store_distance, supermarket_distance, general_hospital_distance, facilities_conditions, shopping_street_distance, drugstore_distance, park_distance, bank_distance, other_facility_name, other_facility_distance)
SELECT id, elementary_school_name, elementary_school_distance, junior_high_school_name, junior_high_school_distance, convenience_store_distance, supermarket_distance, general_hospital_distance, facilities_conditions, shopping_street_distance, drugstore_distance, park_distance, bank_distance, other_facility_name, other_facility_distance
FROM properties
WHERE id IS NOT NULL;

-- 📸 properties_imagesへのデータ移行
INSERT INTO properties_images (property_id, image_type_1, image_comment_1, local_file_name_2, image_type_2, image_comment_2, local_file_name_3, image_type_3, image_comment_3, local_file_name_4, image_type_4, image_comment_4, local_file_name_5, image_type_5, image_comment_5, local_file_name_6, image_type_6, image_comment_6, image_type_7, image_comment_7, local_file_name_8, image_type_8, image_comment_8, local_file_name_9, image_type_9, image_comment_9, local_file_name_10, image_type_10, image_comment_10, local_file_name_11, image_type_11, image_comment_11, local_file_name_12, image_type_12, image_comment_12, local_file_name_13, image_type_13, image_comment_13, local_file_name_14, image_type_14, image_comment_14, local_file_name_15, image_type_15, image_comment_15, local_file_name_16, image_type_16, image_comment_16, local_file_name_17, image_type_17, image_comment_17, local_file_name_18, image_type_18, image_comment_18, local_file_name_19, image_type_19, image_comment_19, local_file_name_20, image_type_20, image_comment_20, local_file_name_21, image_type_21, image_comment_21, local_file_name_22, image_type_22, image_comment_22, local_file_name_23, image_type_23, image_comment_23, local_file_name_24, image_type_24, image_comment_24, local_file_name_25, image_type_25, image_comment_25, local_file_name_26, image_type_26, image_comment_26, local_file_name_27, image_type_27, image_comment_27, local_file_name_28, image_type_28, image_comment_28, local_file_name_29, image_type_29, image_comment_29, local_file_name_30, image_type_30, image_comment_30)
SELECT id, image_type_1, image_comment_1, local_file_name_2, image_type_2, image_comment_2, local_file_name_3, image_type_3, image_comment_3, local_file_name_4, image_type_4, image_comment_4, local_file_name_5, image_type_5, image_comment_5, local_file_name_6, image_type_6, image_comment_6, image_type_7, image_comment_7, local_file_name_8, image_type_8, image_comment_8, local_file_name_9, image_type_9, image_comment_9, local_file_name_10, image_type_10, image_comment_10, local_file_name_11, image_type_11, image_comment_11, local_file_name_12, image_type_12, image_comment_12, local_file_name_13, image_type_13, image_comment_13, local_file_name_14, image_type_14, image_comment_14, local_file_name_15, image_type_15, image_comment_15, local_file_name_16, image_type_16, image_comment_16, local_file_name_17, image_type_17, image_comment_17, local_file_name_18, image_type_18, image_comment_18, local_file_name_19, image_type_19, image_comment_19, local_file_name_20, image_type_20, image_comment_20, local_file_name_21, image_type_21, image_comment_21, local_file_name_22, image_type_22, image_comment_22, local_file_name_23, image_type_23, image_comment_23, local_file_name_24, image_type_24, image_comment_24, local_file_name_25, image_type_25, image_comment_25, local_file_name_26, image_type_26, image_comment_26, local_file_name_27, image_type_27, image_comment_27, local_file_name_28, image_type_28, image_comment_28, local_file_name_29, image_type_29, image_comment_29, local_file_name_30, image_type_30, image_comment_30
FROM properties
WHERE id IS NOT NULL;

COMMIT;
