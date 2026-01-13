-- 防火地域バリデーション修正
-- 実行: ssh rea-conoha "sudo -u postgres psql real_estate_db" < fix_fire_prevention_validation.sql
-- 作成: 2026-01-13
--
-- 問題:
--   fire_prevention_district（未使用、データ0件）がバリデーション対象になっている
--   fire_prevention_area（実使用中）がバリデーション対象外 + shirokumaのみ表示
--
-- 修正:
--   fire_prevention_district → バリデーション無効化
--   fire_prevention_area → バリデーション対象 + 全ユーザーに表示

-- ============================================================================
-- 1. fire_prevention_district のバリデーションを無効化（未使用フィールド）
-- ============================================================================
UPDATE column_labels
SET required_for_publication = NULL,
    updated_at = NOW()
WHERE table_name = 'land_info' AND column_name = 'fire_prevention_district';

-- ============================================================================
-- 2. fire_prevention_area をバリデーション対象 + 全ユーザーに表示
-- ============================================================================
UPDATE column_labels
SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building,land}',
    visible_for = NULL,
    updated_at = NOW()
WHERE table_name = 'land_info' AND column_name = 'fire_prevention_area';

-- ============================================================================
-- 3. 確認クエリ
-- ============================================================================
SELECT column_name, japanese_label, required_for_publication, visible_for
FROM column_labels
WHERE column_name IN ('fire_prevention_district', 'fire_prevention_area')
  AND table_name = 'land_info';
