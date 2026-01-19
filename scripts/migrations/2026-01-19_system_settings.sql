-- システム設定テーブル作成
-- 日付: 2026-01-19
-- 用途: Google Maps APIキー等のシステム設定をDB管理

-- =============================================================================
-- 1. system_settings テーブル作成
-- =============================================================================

CREATE TABLE IF NOT EXISTS system_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER,
    updated_by INTEGER
);

-- コメント追加
COMMENT ON TABLE system_settings IS 'システム設定値を管理するテーブル';
COMMENT ON COLUMN system_settings.key IS '設定キー（一意）';
COMMENT ON COLUMN system_settings.value IS '設定値';
COMMENT ON COLUMN system_settings.is_encrypted IS '暗号化フラグ（将来用）';
COMMENT ON COLUMN system_settings.description IS '設定の説明';

-- =============================================================================
-- 2. 初期データ挿入（Google Maps APIキー用のレコード）
-- =============================================================================

INSERT INTO system_settings (key, value, description, is_encrypted)
VALUES ('GOOGLE_MAPS_API_KEY', NULL, 'Google Maps Geocoding APIキー', FALSE)
ON CONFLICT (key) DO NOTHING;

-- =============================================================================
-- 確認クエリ
-- =============================================================================

SELECT * FROM system_settings;
