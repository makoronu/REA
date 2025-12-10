
-- =====================================================
-- REA マスターデータ管理システム
-- 日本一の不動産システムを目指すマルチテナント対応設計
-- =====================================================

-- 1. マスターカテゴリテーブル（物件種別、建物構造などの分類）
CREATE TABLE IF NOT EXISTS master_categories (
    id SERIAL PRIMARY KEY,
    category_code VARCHAR(50) NOT NULL UNIQUE,      -- 'property_type', 'building_structure'
    category_name VARCHAR(100) NOT NULL,            -- '物件種別', '建物構造'
    description TEXT,                               -- カテゴリの説明
    source VARCHAR(50) DEFAULT 'system',            -- 'homes', 'suumo', 'athome', 'system'
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. マスターオプションテーブル（選択肢の値）
CREATE TABLE IF NOT EXISTS master_options (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES master_categories(id) ON DELETE CASCADE,
    option_code VARCHAR(50) NOT NULL,               -- '1101', '1201' など
    option_value VARCHAR(200) NOT NULL,             -- '売地', '新築戸建' など
    parent_option_id INTEGER REFERENCES master_options(id),  -- 階層構造対応
    source VARCHAR(50) DEFAULT 'homes',             -- データソース
    source_version VARCHAR(20),                     -- 'v4.3.2' など
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    metadata JSONB,                                 -- 追加情報（アイコン、色など）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, option_code)
);

-- 3. 会社別マスター設定テーブル（マルチテナント対応）
CREATE TABLE IF NOT EXISTS company_master_settings (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,                    -- 会社ID（将来のcompaniesテーブル参照）
    category_id INTEGER NOT NULL REFERENCES master_categories(id),
    option_id INTEGER REFERENCES master_options(id),
    custom_value VARCHAR(200),                      -- 会社独自の表示名
    is_enabled BOOLEAN DEFAULT TRUE,                -- この会社で使用可能か
    display_order INTEGER,                          -- 会社別の表示順
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, category_id, option_id)
);

-- 4. ポータルサイトマッピングテーブル（ホームズ/SUUMO/athome変換用）
CREATE TABLE IF NOT EXISTS portal_mappings (
    id SERIAL PRIMARY KEY,
    option_id INTEGER NOT NULL REFERENCES master_options(id),
    portal_name VARCHAR(50) NOT NULL,               -- 'homes', 'suumo', 'athome'
    portal_code VARCHAR(50) NOT NULL,               -- ポータル側のコード
    portal_value VARCHAR(200),                      -- ポータル側の値
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(option_id, portal_name)
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_master_options_category ON master_options(category_id);
CREATE INDEX IF NOT EXISTS idx_master_options_code ON master_options(option_code);
CREATE INDEX IF NOT EXISTS idx_company_settings_company ON company_master_settings(company_id);
CREATE INDEX IF NOT EXISTS idx_portal_mappings_portal ON portal_mappings(portal_name, portal_code);

-- コメント
COMMENT ON TABLE master_categories IS 'マスターデータのカテゴリ管理（物件種別、建物構造など）';
COMMENT ON TABLE master_options IS 'マスターデータの選択肢（ホームズCSV仕様書ベース）';
COMMENT ON TABLE company_master_settings IS '会社別のマスター設定（マルチテナント対応）';
COMMENT ON TABLE portal_mappings IS '各ポータルサイトとのコード変換マッピング';
