-- Seg2: UIマスタ化マイグレーション
-- 実行: ssh rea-conoha "sudo -u postgres psql real_estate_db" < seg2_ui_master.sql

-- =====================================================
-- Step 1: master_optionsに新カラム追加
-- =====================================================

-- is_default: デフォルト値として使用するか
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'master_options' AND column_name = 'is_default'
    ) THEN
        ALTER TABLE master_options ADD COLUMN is_default BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'column is_default added';
    ELSE
        RAISE NOTICE 'column is_default already exists';
    END IF;
END $$;

-- allows_publication: このステータスで公開可能か（販売中・商談中など）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'master_options' AND column_name = 'allows_publication'
    ) THEN
        ALTER TABLE master_options ADD COLUMN allows_publication BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'column allows_publication added';
    ELSE
        RAISE NOTICE 'column allows_publication already exists';
    END IF;
END $$;

-- linked_status: 連動する公開ステータス（販売中→公開、成約済み→非公開など）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'master_options' AND column_name = 'linked_status'
    ) THEN
        ALTER TABLE master_options ADD COLUMN linked_status VARCHAR(50);
        RAISE NOTICE 'column linked_status added';
    ELSE
        RAISE NOTICE 'column linked_status already exists';
    END IF;
END $$;

-- ui_color: UI表示色（bg-green-50 text-green-700 など）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'master_options' AND column_name = 'ui_color'
    ) THEN
        ALTER TABLE master_options ADD COLUMN ui_color VARCHAR(100);
        RAISE NOTICE 'column ui_color added';
    ELSE
        RAISE NOTICE 'column ui_color already exists';
    END IF;
END $$;

-- shows_contractor: 元請会社表示が必要か（専任媒介等）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'master_options' AND column_name = 'shows_contractor'
    ) THEN
        ALTER TABLE master_options ADD COLUMN shows_contractor BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'column shows_contractor added';
    ELSE
        RAISE NOTICE 'column shows_contractor already exists';
    END IF;
END $$;

-- =====================================================
-- Step 2: master_categoriesに新カラム追加
-- =====================================================

-- icon: カテゴリアイコン
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'master_categories' AND column_name = 'icon'
    ) THEN
        ALTER TABLE master_categories ADD COLUMN icon VARCHAR(50);
        RAISE NOTICE 'column icon added';
    ELSE
        RAISE NOTICE 'column icon already exists';
    END IF;
END $$;

-- =====================================================
-- Step 3: 新規マスタカテゴリ追加
-- =====================================================

-- 接道方向
INSERT INTO master_categories (category_code, category_name, description, source, display_order)
VALUES ('road_direction', '接道方向', '道路への接道方向', 'system', 100)
ON CONFLICT (category_code) DO NOTHING;

-- 接道種別
INSERT INTO master_categories (category_code, category_name, description, source, display_order)
VALUES ('road_type', '接道種別', '公道/私道の区分', 'system', 101)
ON CONFLICT (category_code) DO NOTHING;

-- 接道状況
INSERT INTO master_categories (category_code, category_name, description, source, display_order)
VALUES ('road_status', '接道状況', '建築基準法上の道路種別', 'system', 102)
ON CONFLICT (category_code) DO NOTHING;

-- 間取タイプ
INSERT INTO master_categories (category_code, category_name, description, source, display_order)
VALUES ('room_type', '間取タイプ', 'K/DK/LDK等の間取タイプ', 'system', 103)
ON CONFLICT (category_code) DO NOTHING;

-- 防火地域
INSERT INTO master_categories (category_code, category_name, description, source, display_order)
VALUES ('fire_prevention', '防火地域', '防火地域の区分', 'system', 104)
ON CONFLICT (category_code) DO NOTHING;

-- リフォーム項目
INSERT INTO master_categories (category_code, category_name, description, source, display_order)
VALUES ('renovation_item', 'リフォーム項目', 'リフォーム対象項目', 'system', 105)
ON CONFLICT (category_code) DO NOTHING;

-- =====================================================
-- Step 4: 新規マスタオプション追加
-- =====================================================

-- 接道方向（8件）
INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '1', '北', 1 FROM master_categories WHERE category_code = 'road_direction'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '2', '北東', 2 FROM master_categories WHERE category_code = 'road_direction'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '3', '東', 3 FROM master_categories WHERE category_code = 'road_direction'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '4', '南東', 4 FROM master_categories WHERE category_code = 'road_direction'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '5', '南', 5 FROM master_categories WHERE category_code = 'road_direction'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '6', '南西', 6 FROM master_categories WHERE category_code = 'road_direction'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '7', '西', 7 FROM master_categories WHERE category_code = 'road_direction'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '8', '北西', 8 FROM master_categories WHERE category_code = 'road_direction'
ON CONFLICT (category_id, option_code) DO NOTHING;

-- 接道種別（2件）
INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '1', '公道', 1 FROM master_categories WHERE category_code = 'road_type'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '2', '私道', 2 FROM master_categories WHERE category_code = 'road_type'
ON CONFLICT (category_id, option_code) DO NOTHING;

-- 接道状況（6件）
INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '1', '建築基準法上の道路', 1 FROM master_categories WHERE category_code = 'road_status'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '2', '42条1項1号', 2 FROM master_categories WHERE category_code = 'road_status'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '3', '42条1項2号', 3 FROM master_categories WHERE category_code = 'road_status'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '4', '42条1項3号', 4 FROM master_categories WHERE category_code = 'road_status'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '5', '42条2項道路', 5 FROM master_categories WHERE category_code = 'road_status'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '9', 'その他', 9 FROM master_categories WHERE category_code = 'road_status'
ON CONFLICT (category_id, option_code) DO NOTHING;

-- 間取タイプ（9件）
INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '10', 'R', 1 FROM master_categories WHERE category_code = 'room_type'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '20', 'K', 2 FROM master_categories WHERE category_code = 'room_type'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '25', 'SK', 3 FROM master_categories WHERE category_code = 'room_type'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '30', 'DK', 4 FROM master_categories WHERE category_code = 'room_type'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '35', 'SDK', 5 FROM master_categories WHERE category_code = 'room_type'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '40', 'LK', 6 FROM master_categories WHERE category_code = 'room_type'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '45', 'SLK', 7 FROM master_categories WHERE category_code = 'room_type'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '50', 'LDK', 8 FROM master_categories WHERE category_code = 'room_type'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '55', 'SLDK', 9 FROM master_categories WHERE category_code = 'room_type'
ON CONFLICT (category_id, option_code) DO NOTHING;

-- 防火地域（3件）
INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '1', '防火地域', 1 FROM master_categories WHERE category_code = 'fire_prevention'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '2', '準防火地域', 2 FROM master_categories WHERE category_code = 'fire_prevention'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '3', '指定なし', 3 FROM master_categories WHERE category_code = 'fire_prevention'
ON CONFLICT (category_id, option_code) DO NOTHING;

-- リフォーム項目（14件）
INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '1', 'キッチン', 1 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '2', '浴室', 2 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '3', 'トイレ', 3 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '4', '洗面台', 4 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '5', '床', 5 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '6', '壁紙', 6 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '7', '外壁', 7 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '8', '屋根', 8 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '9', '給湯器', 9 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '10', '配管', 10 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '11', '窓・サッシ', 11 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '12', '電気設備', 12 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '13', '防水工事', 13 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

INSERT INTO master_options (category_id, option_code, option_value, display_order)
SELECT id, '99', 'その他', 99 FROM master_categories WHERE category_code = 'renovation_item'
ON CONFLICT (category_id, option_code) DO NOTHING;

-- =====================================================
-- Step 5: 既存マスタの設定更新
-- =====================================================

-- 販売ステータス: is_default, allows_publication, linked_status, ui_color設定
UPDATE master_options SET is_default = TRUE
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'sales_status')
  AND option_value = '査定中';

UPDATE master_options SET allows_publication = TRUE, linked_status = '公開', ui_color = 'bg-green-50 text-green-700'
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'sales_status')
  AND option_value = '販売中';

UPDATE master_options SET allows_publication = TRUE, linked_status = '公開', ui_color = 'bg-yellow-50 text-yellow-700'
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'sales_status')
  AND option_value = '商談中';

UPDATE master_options SET allows_publication = FALSE, linked_status = '非公開', ui_color = 'bg-blue-50 text-blue-700'
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'sales_status')
  AND option_value = '成約済み';

UPDATE master_options SET allows_publication = FALSE, linked_status = '非公開', ui_color = 'bg-gray-100 text-gray-600'
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'sales_status')
  AND option_value = '販売終了';

UPDATE master_options SET allows_publication = FALSE, linked_status = '非公開', ui_color = 'bg-gray-100 text-gray-600'
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'sales_status')
  AND option_value = '取下げ';

UPDATE master_options SET allows_publication = FALSE, linked_status = '非公開', ui_color = 'bg-purple-50 text-purple-700'
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'sales_status')
  AND option_value = '査定中';

-- 公開ステータス: is_default, ui_color設定
UPDATE master_options SET is_default = TRUE, ui_color = 'bg-gray-100 text-gray-600'
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'publication_status')
  AND option_value = '非公開';

UPDATE master_options SET ui_color = 'bg-green-50 text-green-700'
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'publication_status')
  AND option_value = '公開';

UPDATE master_options SET ui_color = 'bg-blue-50 text-blue-700'
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'publication_status')
  AND option_value = '会員公開';

-- 取引形態: shows_contractor設定（専任媒介、一般媒介、専属専任）
UPDATE master_options SET shows_contractor = TRUE
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'transaction_type')
  AND option_value IN ('専任媒介', '一般媒介', '専属専任媒介');

-- カテゴリにアイコン設定
UPDATE master_categories SET icon = '🏠' WHERE category_code = 'property_type';
UPDATE master_categories SET icon = '📊' WHERE category_code = 'sales_status';
UPDATE master_categories SET icon = '📢' WHERE category_code = 'publication_status';
UPDATE master_categories SET icon = '🛤️' WHERE category_code = 'road_direction';
UPDATE master_categories SET icon = '🛣️' WHERE category_code = 'road_type';
UPDATE master_categories SET icon = '📋' WHERE category_code = 'road_status';
UPDATE master_categories SET icon = '🏗️' WHERE category_code = 'room_type';
UPDATE master_categories SET icon = '🔥' WHERE category_code = 'fire_prevention';
UPDATE master_categories SET icon = '🔧' WHERE category_code = 'renovation_item';
UPDATE master_categories SET icon = '📝' WHERE category_code = 'transaction_type';

-- =====================================================
-- 確認クエリ
-- =====================================================

-- 追加カラム確認
SELECT 'master_options新カラム' as check_type, column_name
FROM information_schema.columns
WHERE table_name = 'master_options'
  AND column_name IN ('is_default', 'allows_publication', 'linked_status', 'ui_color', 'shows_contractor');

SELECT 'master_categories新カラム' as check_type, column_name
FROM information_schema.columns
WHERE table_name = 'master_categories'
  AND column_name = 'icon';

-- 新規カテゴリ確認
SELECT 'new_categories' as check_type, category_code, category_name, icon
FROM master_categories
WHERE category_code IN ('road_direction', 'road_type', 'road_status', 'room_type', 'fire_prevention', 'renovation_item');

-- 新規オプション確認（接道方向の例）
SELECT 'road_direction_options' as check_type, option_code, option_value
FROM master_options
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'road_direction')
ORDER BY display_order;

-- 既存マスタ更新確認
SELECT 'sales_status_settings' as check_type, option_value, is_default, allows_publication, linked_status, ui_color
FROM master_options
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'sales_status');

SELECT 'transaction_type_contractor' as check_type, option_value, shows_contractor
FROM master_options
WHERE category_id = (SELECT id FROM master_categories WHERE category_code = 'transaction_type')
  AND shows_contractor = TRUE;
