-- 公開時必須項目設定用カラム追加
-- 実行: psql -d rea_dev -f add_required_for_publication.sql

-- カラム追加（存在しない場合のみ）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'column_labels' AND column_name = 'required_for_publication'
    ) THEN
        ALTER TABLE column_labels ADD COLUMN required_for_publication TEXT[];
        RAISE NOTICE 'column required_for_publication added';
    ELSE
        RAISE NOTICE 'column required_for_publication already exists';
    END IF;
END $$;

-- コメント追加
COMMENT ON COLUMN column_labels.required_for_publication IS '公開時必須の物件種別（NULLは任意、配列で指定種別のみ必須）';
