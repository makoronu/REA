-- road_info: 全物件種別で必須に修正
-- 実行: ssh rea-conoha "sudo -u postgres psql real_estate_db" < 2026-01-14_fix_road_info_required.sql
-- 作成: 2026-01-14
-- 目的: add_land_to_required_for_publication.sqlで建物系8種が消失した問題を修正
-- 背景: road_infoのrequired_for_publicationが{land}のみになり、
--       建物系物件で接道関係バリデーションが無効化されていた

UPDATE column_labels
SET required_for_publication = '{mansion,apartment,detached,office,store,warehouse,factory,building,land}',
    updated_at = NOW()
WHERE table_name = 'land_info' AND column_name = 'road_info';

-- 確認
SELECT column_name, required_for_publication
FROM column_labels
WHERE table_name = 'land_info' AND column_name = 'road_info';

-- ロールバック用:
-- UPDATE column_labels SET required_for_publication = '{land}' WHERE table_name = 'land_info' AND column_name = 'road_info';
