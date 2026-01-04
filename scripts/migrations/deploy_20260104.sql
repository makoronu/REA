-- =====================================================
-- デプロイ 2026-01-04 マイグレーション
-- =====================================================

-- 1. system_config テーブル作成
CREATE TABLE IF NOT EXISTS system_config (
  id SERIAL PRIMARY KEY,
  config_key VARCHAR(255) NOT NULL UNIQUE,
  config_value JSONB,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. column_labels 新カラム追加
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS valid_none_text TEXT[];
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS zero_is_valid BOOLEAN DEFAULT FALSE;
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS conditional_exclusion JSONB;
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS special_flag_key VARCHAR(255);
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS api_endpoint VARCHAR(255);
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS api_field_path VARCHAR(255);
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS placeholder VARCHAR(255);

-- 3. master_categories 新カラム追加
ALTER TABLE master_categories ADD COLUMN IF NOT EXISTS icon VARCHAR(255);

-- 4. master_options 新カラム追加
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS requires_validation BOOLEAN DEFAULT FALSE;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS allows_publication BOOLEAN DEFAULT FALSE;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS linked_status VARCHAR(255);
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS ui_color VARCHAR(50);
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS shows_contractor BOOLEAN DEFAULT FALSE;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS api_aliases JSONB;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS triggers_unpublish BOOLEAN DEFAULT FALSE;
ALTER TABLE master_options ADD COLUMN IF NOT EXISTS triggers_pre_check BOOLEAN DEFAULT FALSE;

-- 5. property_types 新カラム追加
ALTER TABLE property_types ADD COLUMN IF NOT EXISTS sort_order INTEGER;

-- 6. land_info 型変更 (integer → jsonb)
-- use_district
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_name = 'land_info' AND column_name = 'use_district'
             AND data_type = 'integer') THEN
    ALTER TABLE land_info ADD COLUMN use_district_new JSONB;
    UPDATE land_info SET use_district_new = to_jsonb(ARRAY[use_district]) WHERE use_district IS NOT NULL;
    ALTER TABLE land_info DROP COLUMN use_district;
    ALTER TABLE land_info RENAME COLUMN use_district_new TO use_district;
  END IF;
END $$;

-- city_planning
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns
             WHERE table_name = 'land_info' AND column_name = 'city_planning'
             AND data_type = 'integer') THEN
    ALTER TABLE land_info ADD COLUMN city_planning_new JSONB;
    UPDATE land_info SET city_planning_new = to_jsonb(ARRAY[city_planning]) WHERE city_planning IS NOT NULL;
    ALTER TABLE land_info DROP COLUMN city_planning;
    ALTER TABLE land_info RENAME COLUMN city_planning_new TO city_planning;
  END IF;
END $$;

-- 確認
SELECT 'Migration completed' AS status;
