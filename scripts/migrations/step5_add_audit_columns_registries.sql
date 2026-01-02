-- Step 5準備: 登記関連テーブルに監査カラム追加
-- 実行日: 2026-01-02
-- 目的: registries.py, touki.pyの論理削除対応

-- 1. registry_kou_entries（甲区エントリ）
ALTER TABLE registry_kou_entries ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE registry_kou_entries ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE registry_kou_entries ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);

-- 2. registry_otsu_entries（乙区エントリ）
ALTER TABLE registry_otsu_entries ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE registry_otsu_entries ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE registry_otsu_entries ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);

-- 3. touki_records（登記レコード）
ALTER TABLE touki_records ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE touki_records ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE touki_records ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);

-- 4. touki_imports（登記インポート）
ALTER TABLE touki_imports ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE touki_imports ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE touki_imports ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);

-- インデックス作成（deleted_at検索用）
CREATE INDEX IF NOT EXISTS idx_registry_kou_entries_deleted_at ON registry_kou_entries(deleted_at);
CREATE INDEX IF NOT EXISTS idx_registry_otsu_entries_deleted_at ON registry_otsu_entries(deleted_at);
CREATE INDEX IF NOT EXISTS idx_touki_records_deleted_at ON touki_records(deleted_at);
CREATE INDEX IF NOT EXISTS idx_touki_imports_deleted_at ON touki_imports(deleted_at);
