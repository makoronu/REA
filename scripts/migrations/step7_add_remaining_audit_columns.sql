-- Step 7: 残り18テーブルへの監査カラム追加
-- 実行日: 2026-01-02
-- 目的: プロトコル準拠（created_at, updated_at, created_by, updated_by, deleted_at必須）

-- ========================================
-- 1. company_master_settings
-- ========================================
ALTER TABLE company_master_settings ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE company_master_settings ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE company_master_settings ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_company_master_settings_deleted_at ON company_master_settings(deleted_at);

-- ========================================
-- 2. import_field_mappings
-- ========================================
ALTER TABLE import_field_mappings ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE import_field_mappings ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE import_field_mappings ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_import_field_mappings_deleted_at ON import_field_mappings(deleted_at);

-- ========================================
-- 3. import_value_mappings
-- ========================================
ALTER TABLE import_value_mappings ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE import_value_mappings ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE import_value_mappings ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_import_value_mappings_deleted_at ON import_value_mappings(deleted_at);

-- ========================================
-- 4. m_city_planning
-- ========================================
ALTER TABLE m_city_planning ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE m_city_planning ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE m_city_planning ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE m_city_planning ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_m_city_planning_deleted_at ON m_city_planning(deleted_at);

-- ========================================
-- 5. m_data_sources
-- ========================================
ALTER TABLE m_data_sources ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE m_data_sources ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE m_data_sources ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_m_data_sources_deleted_at ON m_data_sources(deleted_at);

-- ========================================
-- 6. m_facility_categories
-- ========================================
ALTER TABLE m_facility_categories ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE m_facility_categories ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE m_facility_categories ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE m_facility_categories ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_m_facility_categories_deleted_at ON m_facility_categories(deleted_at);

-- ========================================
-- 7. m_integrations
-- ========================================
ALTER TABLE m_integrations ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE m_integrations ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE m_integrations ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_m_integrations_deleted_at ON m_integrations(deleted_at);

-- ========================================
-- 8. m_postal_codes
-- ========================================
ALTER TABLE m_postal_codes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE m_postal_codes ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE m_postal_codes ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE m_postal_codes ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_m_postal_codes_deleted_at ON m_postal_codes(deleted_at);

-- ========================================
-- 9. m_registry_purposes
-- ========================================
ALTER TABLE m_registry_purposes ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE m_registry_purposes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE m_registry_purposes ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE m_registry_purposes ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE m_registry_purposes ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_m_registry_purposes_deleted_at ON m_registry_purposes(deleted_at);

-- ========================================
-- 10. m_roles
-- ========================================
ALTER TABLE m_roles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE m_roles ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE m_roles ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE m_roles ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_m_roles_deleted_at ON m_roles(deleted_at);

-- ========================================
-- 11. m_stations
-- ========================================
ALTER TABLE m_stations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE m_stations ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE m_stations ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE m_stations ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_m_stations_deleted_at ON m_stations(deleted_at);

-- ========================================
-- 12. master_categories
-- ========================================
ALTER TABLE master_categories ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE master_categories ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE master_categories ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_master_categories_deleted_at ON master_categories(deleted_at);

-- ========================================
-- 13. master_options
-- ========================================
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_master_options_deleted_at ON master_options(deleted_at);

-- ========================================
-- 14. organizations
-- ========================================
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_organizations_deleted_at ON organizations(deleted_at);

-- ========================================
-- 15. portal_mappings
-- ========================================
ALTER TABLE portal_mappings ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE portal_mappings ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE portal_mappings ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE portal_mappings ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_portal_mappings_deleted_at ON portal_mappings(deleted_at);

-- ========================================
-- 16. property_touki_links
-- ========================================
ALTER TABLE property_touki_links ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE property_touki_links ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE property_touki_links ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE property_touki_links ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_property_touki_links_deleted_at ON property_touki_links(deleted_at);

-- ========================================
-- 17. property_types
-- ========================================
ALTER TABLE property_types ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE property_types ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE property_types ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_property_types_deleted_at ON property_types(deleted_at);

-- ========================================
-- 18. users
-- ========================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users(deleted_at);

-- ========================================
-- 確認クエリ
-- ========================================
-- SELECT table_name, column_name
-- FROM information_schema.columns
-- WHERE column_name IN ('created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_at')
-- AND table_schema = 'public'
-- ORDER BY table_name, column_name;
