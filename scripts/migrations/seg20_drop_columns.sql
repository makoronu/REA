-- Seg 20: DBカラム物理DROP（コードデプロイ後に実行）
-- 前提: images.py/generic.py からuploaded_at参照が削除済みであること

-- properties.geom（PostGIS geometry型、データ0件、コード参照0）
ALTER TABLE properties DROP COLUMN IF EXISTS geom;

-- land_info.land_law_permission（データ全NULL、コード参照0）
ALTER TABLE land_info DROP COLUMN IF EXISTS land_law_permission;

-- property_images.uploaded_at（データ0件、コード参照削除済み）
ALTER TABLE property_images DROP COLUMN IF EXISTS uploaded_at;
