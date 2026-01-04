-- Seg5バグ修正: triggers_unpublishカラム追加
-- 実行: ssh rea-conoha "sudo -u postgres psql real_estate_db" < seg5_triggers_unpublish.sql

-- =====================================================
-- Step 1: master_optionsにtriggers_unpublishカラム追加
-- =====================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'master_options' AND column_name = 'triggers_unpublish'
    ) THEN
        ALTER TABLE master_options ADD COLUMN triggers_unpublish BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'column triggers_unpublish added';
    ELSE
        RAISE NOTICE 'column triggers_unpublish already exists';
    END IF;
END $$;

-- =====================================================
-- Step 2: データ設定（成約済み、取下げ、販売終了 → 非公開連動）
-- =====================================================

UPDATE master_options SET triggers_unpublish = TRUE
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'sales_status')
  AND option_value IN ('成約済み', '取下げ', '販売終了');

-- =====================================================
-- 確認クエリ
-- =====================================================

SELECT 'triggers_unpublish設定' as check_type, option_value, triggers_unpublish
FROM master_options
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'sales_status');
