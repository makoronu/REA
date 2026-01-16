-- Seg3b-2: 旧月額費用カラムのバリデーション設定クリーンアップ
-- 実行日: 2026-01-16
-- 目的: 非表示カラム（management_fee, repair_reserve_fund, repair_reserve_fund_base）の
--       required_for_publicationとzero_is_validをNULL/falseに設定

-- 変更前の状態を確認
SELECT column_name, visible_for, required_for_publication, zero_is_valid
FROM column_labels
WHERE column_name IN ('management_fee', 'repair_reserve_fund', 'repair_reserve_fund_base', 'monthly_costs');

-- 旧カラムのrequired_for_publicationをNULLに
UPDATE column_labels
SET required_for_publication = NULL,
    zero_is_valid = false,
    updated_at = NOW()
WHERE column_name IN ('management_fee', 'repair_reserve_fund', 'repair_reserve_fund_base')
  AND visible_for = '{}';

-- 変更後の状態を確認
SELECT column_name, visible_for, required_for_publication, zero_is_valid
FROM column_labels
WHERE column_name IN ('management_fee', 'repair_reserve_fund', 'repair_reserve_fund_base', 'monthly_costs');
