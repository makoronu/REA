-- REA Database Split: Permissions Setup
-- Generated: 2025-07-21 15:30:18

BEGIN;

-- properties_location 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_location TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_location_id_seq TO rea_user;

-- properties_other 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_other TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_other_id_seq TO rea_user;

-- properties_building 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_building TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_building_id_seq TO rea_user;

-- properties_pricing 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_pricing TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_pricing_id_seq TO rea_user;

-- properties_facilities 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_facilities TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_facilities_id_seq TO rea_user;

-- properties_contract 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_contract TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_contract_id_seq TO rea_user;

-- properties_images 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_images TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_images_id_seq TO rea_user;

-- properties_renovation 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_renovation TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_renovation_id_seq TO rea_user;

-- properties_energy 権限設定
GRANT ALL PRIVILEGES ON TABLE properties_energy TO rea_user;
GRANT USAGE, SELECT ON SEQUENCE properties_energy_id_seq TO rea_user;

COMMIT;
