-- 公開時バリデーション「該当なし」オプション追加
-- 実行日: 2026-01-02
-- Segment A: マスタデータ追加

-- ========================================
-- A-1: 用途地域に「指定なし」追加
-- ========================================
INSERT INTO master_options (
    category_id,
    option_code,
    option_value,
    display_order,
    is_active,
    source
) VALUES (
    40,           -- zoning_district
    'none',
    '指定なし',
    99,
    true,
    'rea'
);

-- ========================================
-- A-2: 向きに「該当なし」追加
-- ========================================
INSERT INTO master_options (
    category_id,
    option_code,
    option_value,
    display_order,
    is_active,
    source
) VALUES (
    18,           -- orientation
    'na',
    '該当なし',
    99,
    true,
    'rea'
);

-- ========================================
-- A-3: 管理形態に「該当なし」追加
-- ========================================
INSERT INTO master_options (
    category_id,
    option_code,
    option_value,
    display_order,
    is_active,
    source
) VALUES (
    16,           -- management_type
    'na',
    '該当なし（戸建等）',
    99,
    true,
    'rea'
);

-- ========================================
-- 確認クエリ
-- ========================================
-- SELECT mc.category_code, mo.option_code, mo.option_value
-- FROM master_options mo
-- JOIN master_categories mc ON mo.category_id = mc.id
-- WHERE mo.source = 'rea' AND mo.option_code IN ('none', 'na');

-- ========================================
-- ロールバック（必要時のみ実行）
-- ========================================
-- DELETE FROM master_options WHERE category_id = 40 AND option_code = 'none' AND source = 'rea';
-- DELETE FROM master_options WHERE category_id = 18 AND option_code = 'na' AND source = 'rea';
-- DELETE FROM master_options WHERE category_id = 16 AND option_code = 'na' AND source = 'rea';
