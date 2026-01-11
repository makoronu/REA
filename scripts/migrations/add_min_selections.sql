-- min_selections カラム追加
-- 目的: multi_selectフィールドで最低選択数をDBで管理
-- 実行: ssh rea-conoha "sudo -u postgres psql real_estate_db" < add_min_selections.sql

-- =====================================================
-- Step 1: column_labelsにmin_selectionsカラム追加
-- =====================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'column_labels' AND column_name = 'min_selections'
    ) THEN
        ALTER TABLE column_labels ADD COLUMN min_selections INTEGER DEFAULT NULL;
        RAISE NOTICE 'column min_selections added';
    ELSE
        RAISE NOTICE 'column min_selections already exists';
    END IF;
END $$;

-- =====================================================
-- Step 2: multi_selectフィールドにmin_selections=1を設定
-- =====================================================

-- input_type='multi_select' かつ required_for_publication が設定されているフィールド
UPDATE column_labels
SET min_selections = 1
WHERE input_type = 'multi_select'
  AND required_for_publication IS NOT NULL
  AND array_length(required_for_publication, 1) > 0;

-- =====================================================
-- 確認クエリ
-- =====================================================

-- 追加カラム確認
SELECT 'min_selections追加確認' as check_type, column_name, data_type
FROM information_schema.columns
WHERE table_name = 'column_labels'
  AND column_name = 'min_selections';

-- 設定されたフィールド確認
SELECT 'min_selections設定フィールド' as check_type,
       table_name,
       column_name,
       input_type,
       min_selections,
       required_for_publication
FROM column_labels
WHERE min_selections IS NOT NULL
ORDER BY table_name, column_name;
