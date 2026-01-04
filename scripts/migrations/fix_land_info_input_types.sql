-- land_info カラムの input_type 修正
-- 問題: multi_select だが DB型が integer のカラムがある
-- 解決: radio に変更（単一選択）

-- city_planning: multi_select → radio（実行済み）
UPDATE column_labels
SET input_type = 'radio'
WHERE table_name = 'land_info'
  AND column_name = 'city_planning'
  AND input_type = 'multi_select';

-- land_category: multi_select → radio
UPDATE column_labels
SET input_type = 'radio'
WHERE table_name = 'land_info'
  AND column_name = 'land_category'
  AND input_type = 'multi_select';

-- 確認
SELECT column_name, input_type
FROM column_labels
WHERE table_name = 'land_info'
  AND column_name IN ('city_planning', 'land_category');
