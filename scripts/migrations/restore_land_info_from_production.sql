-- land_info 7カラムを本番DBから復旧
-- 使用方法: 本番DBに接続して実行後、結果をローカルに反映

-- Step 1: 本番DBで実行してデータを取得
-- psql -h <prod_host> -d <prod_db> -c "COPY (...) TO STDOUT" > land_info_backup.csv

/*
本番DBで以下を実行:

COPY (
  SELECT
    property_id,
    setback,
    terrain,
    city_planning,
    land_category,
    land_rights,
    land_transaction_notice,
    land_area_measurement
  FROM land_info
  WHERE deleted_at IS NULL
) TO '/tmp/land_info_backup.csv' WITH CSV HEADER;
*/

-- Step 2: ローカルで一時テーブル作成・インポート
/*
CREATE TEMP TABLE land_info_restore (
  property_id INTEGER,
  setback INTEGER,
  terrain INTEGER,
  city_planning INTEGER,
  land_category INTEGER,
  land_rights INTEGER,
  land_transaction_notice INTEGER,
  land_area_measurement INTEGER
);

\copy land_info_restore FROM 'land_info_backup.csv' WITH CSV HEADER;

-- Step 3: 更新
UPDATE land_info li
SET
  setback = r.setback,
  terrain = r.terrain,
  city_planning = r.city_planning,
  land_category = r.land_category,
  land_rights = r.land_rights,
  land_transaction_notice = r.land_transaction_notice,
  land_area_measurement = r.land_area_measurement
FROM land_info_restore r
WHERE li.property_id = r.property_id;

DROP TABLE land_info_restore;
*/

-- 注意: 本番DBへのアクセスはユーザーが手動で実施すること
