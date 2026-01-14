-- 土地/駐車場/その他では「居住用/事業用/投資用」を非表示に
-- 建物系8種のみで表示・バリデーション適用

UPDATE column_labels
SET visible_for = '{office,warehouse,factory,store,apartment,mansion,detached,building}'
WHERE column_name IN ('is_residential', 'is_commercial', 'is_investment');

-- ロールバック用:
-- UPDATE column_labels SET visible_for = NULL WHERE column_name IN ('is_residential', 'is_commercial', 'is_investment');
