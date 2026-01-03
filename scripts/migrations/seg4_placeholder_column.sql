-- Seg4: column_labelsにplaceholderカラム追加
-- 実行日: 2026-01-04
-- 目的: 動的フィールドのplaceholderをDB管理化

-- 1. placeholderカラム追加
ALTER TABLE column_labels ADD COLUMN IF NOT EXISTS placeholder VARCHAR(255);

-- 2. コメント追加
COMMENT ON COLUMN column_labels.placeholder IS 'フォームに表示するplaceholderテキスト';

-- 確認クエリ
-- SELECT column_name, placeholder FROM column_labels WHERE placeholder IS NOT NULL;
