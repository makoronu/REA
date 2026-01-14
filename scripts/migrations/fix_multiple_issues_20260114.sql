-- 複数バグ修正マイグレーション
-- 実行: ssh rea-conoha "sudo -u postgres psql real_estate_db" < fix_multiple_issues_20260114.sql
-- 作成: 2026-01-14
--
-- 修正内容:
-- Seg1: 防火地域重複解消（fire_prevention_districtを非表示）
-- Seg3: 設定項目バリデーション用のvalidation_group追加

-- ============================================================================
-- Seg1: fire_prevention_district を非表示に
-- ============================================================================
-- 理由: fire_prevention_area（法令制限タブ）と重複しているため
UPDATE column_labels
SET visible_for = '{}',
    updated_at = NOW()
WHERE table_name = 'land_info' AND column_name = 'fire_prevention_district';

-- ============================================================================
-- Seg3: 設定項目バリデーション用 validation_group カラム追加
-- ============================================================================
-- 同じvalidation_groupを持つフィールドは「いずれか1つtrue」を要求
ALTER TABLE column_labels
ADD COLUMN IF NOT EXISTS validation_group VARCHAR(50);

COMMENT ON COLUMN column_labels.validation_group IS '同じグループのフィールドは「いずれか1つtrue」を要求（例: property_purpose）';

-- is_residential, is_commercial, is_investment に validation_group を設定
UPDATE column_labels
SET validation_group = 'property_purpose',
    updated_at = NOW()
WHERE column_name IN ('is_residential', 'is_commercial', 'is_investment');

-- ============================================================================
-- 確認クエリ
-- ============================================================================
-- Seg1確認
SELECT column_name, japanese_label, visible_for, group_name
FROM column_labels
WHERE column_name = 'fire_prevention_district';

-- Seg3確認
SELECT column_name, japanese_label, validation_group
FROM column_labels
WHERE validation_group IS NOT NULL;
