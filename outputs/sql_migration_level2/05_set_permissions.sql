-- REA Database Split Level 2: Permissions Setup
-- Generated: 2025-07-21 16:02:13

BEGIN;

-- properties_building 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_building TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_building_id_seq TO rea_user;

-- properties_location 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_location TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_location_id_seq TO rea_user;

-- properties_transportation 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_transportation TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_transportation_id_seq TO rea_user;

-- properties_other 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_other TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_other_id_seq TO rea_user;

-- properties_roads 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_roads TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_roads_id_seq TO rea_user;

-- properties_floor_plans 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_floor_plans TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_floor_plans_id_seq TO rea_user;

-- properties_pricing 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_pricing TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_pricing_id_seq TO rea_user;

-- properties_contract 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_contract TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_contract_id_seq TO rea_user;

-- properties_facilities 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_facilities TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_facilities_id_seq TO rea_user;

-- properties_images 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_images TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_images_id_seq TO rea_user;

COMMIT;
