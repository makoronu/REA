-- Seg 27: 現況（current_status）土地用オプション追加
-- 目的: 土地物件で「更地」「古屋あり」「古屋あり更地引渡可」を選択可能にする
-- 影響: master_options INSERT 4件、column_labels UPDATE 1件、properties UPDATE(0→NULL) 146件
-- ロールバック: 本ファイル末尾にROLLBACK SQLあり

BEGIN;

-- ===================================================
-- 1. 新規master_options追加（source='rea'、土地+建物用）
-- ===================================================
-- category_id=2 は current_status

-- rea_4: 未完成（建物系、HOMES code 4）
INSERT INTO master_options (
    category_id, option_code, option_value, source,
    display_order, is_active, is_default,
    created_at, updated_at
) VALUES (
    2, 'rea_4', '未完成', 'rea',
    4, true, false,
    NOW(), NOW()
);

-- rea_5: 更地（土地用、HOMES code 1）
INSERT INTO master_options (
    category_id, option_code, option_value, source,
    display_order, is_active, is_default,
    created_at, updated_at
) VALUES (
    2, 'rea_5', '更地', 'rea',
    5, true, false,
    NOW(), NOW()
);

-- rea_6: 古屋あり（土地用、HOMES code 2）
INSERT INTO master_options (
    category_id, option_code, option_value, source,
    display_order, is_active, is_default,
    created_at, updated_at
) VALUES (
    2, 'rea_6', '古屋あり', 'rea',
    6, true, false,
    NOW(), NOW()
);

-- rea_7: 古屋あり更地引渡可（土地用、HOMES code 10）
INSERT INTO master_options (
    category_id, option_code, option_value, source,
    display_order, is_active, is_default,
    created_at, updated_at
) VALUES (
    2, 'rea_7', '古屋あり更地引渡可', 'rea',
    7, true, false,
    NOW(), NOW()
);

-- ===================================================
-- 2. rea_9（その他）の表示順を最後に移動
-- ===================================================
UPDATE master_options
SET display_order = 8, updated_at = NOW()
WHERE category_id = 2
  AND option_code = 'rea_9'
  AND source = 'rea';

-- ===================================================
-- 3. 孤立エントリ削除（source='REA' 大文字、未使用）
-- ===================================================
-- option_code='0'（未設定）→ 対応データは手順4でNULL化
-- option_code='9'（その他）→ rea_9と重複
DELETE FROM master_options
WHERE category_id = 2
  AND source = 'REA'
  AND option_code IN ('0', '9');

-- ===================================================
-- 4. 既存データ: current_status=0（未設定）→ NULL化
-- ===================================================
UPDATE properties
SET current_status = NULL, updated_at = NOW()
WHERE current_status = 0
  AND deleted_at IS NULL;

-- ===================================================
-- 5. column_labels更新
-- ===================================================
-- input_type: multi_select → radio（現況は単一選択）
-- min_selections: 1 → NULL（radioには不要）
UPDATE column_labels
SET input_type = 'radio',
    min_selections = NULL,
    updated_at = NOW()
WHERE table_name = 'properties'
  AND column_name = 'current_status';

COMMIT;

-- ===================================================
-- 検証クエリ
-- ===================================================
-- master_options確認
-- SELECT mo.option_code, mo.option_value, mo.source, mo.display_order
-- FROM master_options mo
-- JOIN master_categories mc ON mo.category_id = mc.id
-- WHERE mc.category_code = 'current_status'
--   AND mo.deleted_at IS NULL
-- ORDER BY mo.source, mo.display_order;

-- データ分布確認
-- SELECT current_status, COUNT(*) FROM properties
-- WHERE deleted_at IS NULL GROUP BY current_status ORDER BY current_status;

-- column_labels確認
-- SELECT input_type, min_selections, master_category_code
-- FROM column_labels
-- WHERE table_name = 'properties' AND column_name = 'current_status';

-- ===================================================
-- ロールバック（必要時のみ）
-- ===================================================
-- DELETE FROM master_options WHERE category_id = 2 AND option_code IN ('rea_4', 'rea_5', 'rea_6', 'rea_7');
-- UPDATE master_options SET display_order = 4 WHERE category_id = 2 AND option_code = 'rea_9';
-- INSERT INTO master_options (category_id, option_code, option_value, source, display_order, is_active, created_at, updated_at)
--   VALUES (2, '0', '未設定', 'REA', 0, true, NOW(), NOW()),
--          (2, '9', 'その他', 'REA', 0, true, NOW(), NOW());
-- UPDATE properties SET current_status = 0 WHERE current_status IS NULL AND deleted_at IS NULL;
-- UPDATE column_labels SET input_type = 'multi_select', min_selections = 1 WHERE table_name = 'properties' AND column_name = 'current_status';
