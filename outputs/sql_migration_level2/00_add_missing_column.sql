-- REA Database: Missing Column Addition
-- Generated: 2025-07-21 16:02:13
-- local_file_name_1 カラムの追加

BEGIN;

-- local_file_name_1 カラムを追加（image_type_1の前に配置）
ALTER TABLE properties 
ADD COLUMN local_file_name_1 character varying;

-- コメント追加
COMMENT ON COLUMN properties.local_file_name_1 IS '画像ファイル名1（設計時漏れ修正）';

COMMIT;

-- 確認SQL
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'properties' AND column_name LIKE 'local_file_name%' ORDER BY column_name;
