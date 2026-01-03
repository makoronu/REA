-- Seg1: ハードコーディング撲滅マイグレーション
-- 実行: ssh rea-conoha "sudo -u postgres psql real_estate_db" < seg1_hardcoding_elimination.sql

-- =====================================================
-- Step 1: column_labelsに4カラム追加
-- =====================================================

-- valid_none_text: 「なし」として有効なテキスト値の配列
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'column_labels' AND column_name = 'valid_none_text'
    ) THEN
        ALTER TABLE column_labels ADD COLUMN valid_none_text TEXT[];
        RAISE NOTICE 'column valid_none_text added';
    ELSE
        RAISE NOTICE 'column valid_none_text already exists';
    END IF;
END $$;

-- zero_is_valid: 0が有効値となるか
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'column_labels' AND column_name = 'zero_is_valid'
    ) THEN
        ALTER TABLE column_labels ADD COLUMN zero_is_valid BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'column zero_is_valid added';
    ELSE
        RAISE NOTICE 'column zero_is_valid already exists';
    END IF;
END $$;

-- conditional_exclusion: 条件付き除外ルール（JSONB）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'column_labels' AND column_name = 'conditional_exclusion'
    ) THEN
        ALTER TABLE column_labels ADD COLUMN conditional_exclusion JSONB;
        RAISE NOTICE 'column conditional_exclusion added';
    ELSE
        RAISE NOTICE 'column conditional_exclusion already exists';
    END IF;
END $$;

-- special_flag_key: 特殊フラグのキー名
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'column_labels' AND column_name = 'special_flag_key'
    ) THEN
        ALTER TABLE column_labels ADD COLUMN special_flag_key VARCHAR(50);
        RAISE NOTICE 'column special_flag_key added';
    ELSE
        RAISE NOTICE 'column special_flag_key already exists';
    END IF;
END $$;

-- =====================================================
-- Step 2: master_optionsに1カラム追加
-- =====================================================

-- requires_validation: バリデーションが必要なステータスか
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'master_options' AND column_name = 'requires_validation'
    ) THEN
        ALTER TABLE master_options ADD COLUMN requires_validation BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'column requires_validation added';
    ELSE
        RAISE NOTICE 'column requires_validation already exists';
    END IF;
END $$;

-- =====================================================
-- Step 3: データ移行
-- =====================================================

-- 3-1: zero_is_valid 設定（管理費・修繕積立金は0が有効）
UPDATE column_labels SET zero_is_valid = TRUE
WHERE column_name IN ('management_fee', 'repair_reserve_fund')
  AND table_name = 'properties';

-- 3-2: conditional_exclusion 設定
-- 用途地域「指定なし」→ 建ぺい率不要
UPDATE column_labels SET conditional_exclusion = '{"depends_on": "use_district", "exclude_when": ["none", "指定なし"]}'
WHERE column_name = 'building_coverage_ratio' AND table_name = 'properties';

-- 用途地域「指定なし」→ 容積率不要
UPDATE column_labels SET conditional_exclusion = '{"depends_on": "use_district", "exclude_when": ["none", "指定なし"]}'
WHERE column_name = 'floor_area_ratio' AND table_name = 'properties';

-- 戸建 → 所在階不要
UPDATE column_labels SET conditional_exclusion = '{"depends_on": "property_type", "exclude_when": ["detached"]}'
WHERE column_name = 'room_floor' AND table_name = 'properties';

-- 戸建 → 総戸数不要
UPDATE column_labels SET conditional_exclusion = '{"depends_on": "property_type", "exclude_when": ["detached"]}'
WHERE column_name = 'total_units' AND table_name = 'properties';

-- 接道なし → セットバック不要（special_flag_key方式）
UPDATE column_labels SET conditional_exclusion = '{"depends_on": "road_info", "exclude_when_flag": "no_road_access"}'
WHERE column_name = 'setback' AND table_name = 'properties';

-- 3-3: special_flag_key 設定
UPDATE column_labels SET special_flag_key = 'no_road_access' WHERE column_name = 'road_info' AND table_name = 'properties';
UPDATE column_labels SET special_flag_key = 'no_station' WHERE column_name = 'transportation' AND table_name = 'properties';
UPDATE column_labels SET special_flag_key = 'no_bus' WHERE column_name = 'bus_stops' AND table_name = 'properties';
UPDATE column_labels SET special_flag_key = 'no_facilities' WHERE column_name = 'nearby_facilities' AND table_name = 'properties';

-- 3-4: requires_validation 設定（公開・会員公開はバリデーション必要）
UPDATE master_options SET requires_validation = TRUE
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'publication_status')
  AND option_value IN ('公開', '会員公開');

-- =====================================================
-- 確認クエリ
-- =====================================================

-- 追加カラム確認
SELECT 'column_labels新カラム' as check_type, column_name
FROM information_schema.columns
WHERE table_name = 'column_labels'
  AND column_name IN ('valid_none_text', 'zero_is_valid', 'conditional_exclusion', 'special_flag_key');

SELECT 'master_options新カラム' as check_type, column_name
FROM information_schema.columns
WHERE table_name = 'master_options'
  AND column_name = 'requires_validation';

-- データ確認
SELECT 'zero_is_valid設定' as check_type, column_name, zero_is_valid
FROM column_labels WHERE zero_is_valid = TRUE;

SELECT 'conditional_exclusion設定' as check_type, column_name, conditional_exclusion
FROM column_labels WHERE conditional_exclusion IS NOT NULL;

SELECT 'special_flag_key設定' as check_type, column_name, special_flag_key
FROM column_labels WHERE special_flag_key IS NOT NULL;

SELECT 'requires_validation設定' as check_type, option_value, requires_validation
FROM master_options
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'publication_status');
