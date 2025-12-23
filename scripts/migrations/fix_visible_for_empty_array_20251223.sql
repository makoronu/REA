-- visible_for空配列修正
-- 症状: 空配列'{}'だとフロントエンドで非表示と判定される
-- 修正: NULLに変更（NULL=全物件種別表示）

-- 1. NOT NULL制約を削除
ALTER TABLE column_labels ALTER COLUMN visible_for DROP NOT NULL;

-- 2. 空配列をNULLに変更
UPDATE column_labels SET visible_for = NULL WHERE visible_for = '{}';

-- ロールバック手順:
-- UPDATE column_labels SET visible_for = '{}' WHERE visible_for IS NULL;
-- ALTER TABLE column_labels ALTER COLUMN visible_for SET NOT NULL;
