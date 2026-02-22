-- Seg 20: 不要フィールド物理削除
-- 実行順序: 1. このSQL → 2. コードデプロイ → 3. seg20_drop_columns.sql

-- ============================================
-- Step 1: column_labels 物理DELETE（14件）
-- ============================================

-- properties テーブル（2件）
DELETE FROM column_labels WHERE table_name = 'properties' AND column_name = 'geom';
DELETE FROM column_labels WHERE table_name = 'properties' AND column_name = 'zoho_sync_status';

-- land_info テーブル（1件）
DELETE FROM column_labels WHERE table_name = 'land_info' AND column_name = 'land_law_permission';

-- property_images テーブル（11件 — 'images'は残す）
DELETE FROM column_labels WHERE table_name = 'property_images' AND column_name IN (
  'id', 'property_id', 'created_at', 'updated_at',
  'file_path', 'file_url', 'display_order',
  'uploaded_at', 'image_type', 'is_public', 'caption'
);
