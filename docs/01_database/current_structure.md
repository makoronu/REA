# REAデータベース構造

生成日時: 2025-09-11 20:01:53
データベース: real_estate_db
テーブル数: 15

## テーブル一覧

| テーブル名 | カラム数 | レコード数 | 用途 |
|------------|----------|------------|------|
| amenities | 29 | 0 | 不明 |
| building_info | 30 | 0 | 不明 |
| building_structure | 6 | 12 | 建物構造 |
| column_labels | 13 | 143 | カラムメタデータ |
| current_status | 6 | 9 | 現況 |
| equipment_master | 10 | 14 | 設備マスター |
| floor_plan_room_types | 6 | 9 | 間取りタイプ |
| image_types | 6 | 22 | 画像種別 |
| land_info | 29 | 0 | 不明 |
| land_rights | 6 | 12 | 土地権利 |
| properties | 44 | 0 | 物件情報 |
| property_equipment | 6 | 0 | 物件-設備関連 |
| property_images | 11 | 0 | 不明 |
| property_types | 6 | 14 | 物件種別 |
| zoning_districts | 6 | 14 | 用途地域 |

総カラム数: 214

## テーブル詳細

### amenities
- カラム数: 29
- レコード数: 0

| カラム名 | データ型 |
|----------|----------|
| id | integer |
| property_id | integer |
| facilities | jsonb |
| property_features | text |
| notes | text |
| transportation | jsonb |
| other_transportation | character varying |
| elementary_school_name | character varying |
| elementary_school_distance | integer |
| junior_high_school_name | character varying |

他 19 カラム

### building_info
- カラム数: 30
- レコード数: 0

| カラム名 | データ型 |
|----------|----------|
| id | integer |
| property_id | integer |
| building_structure | USER-DEFINED |
| construction_date | date |
| building_floors_above | integer |
| building_floors_below | integer |
| total_units | integer |
| total_site_area | numeric |
| building_area | numeric |
| total_floor_area | numeric |

他 20 カラム

### building_structure
- カラム数: 6
- レコード数: 12

| カラム名 | データ型 |
|----------|----------|
| id | character varying |
| label | character varying |
| group_name | character varying |
| homes_id | integer |
| created_at | timestamp without time zone |
| updated_at | timestamp without time zone |

### column_labels
- カラム数: 13
- レコード数: 143

| カラム名 | データ型 |
|----------|----------|
| table_name | character varying |
| column_name | character varying |
| japanese_label | character varying |
| description | text |
| data_type | character varying |
| is_required | boolean |
| display_order | integer |
| group_name | character varying |
| input_type | character varying |
| max_length | integer |

他 3 カラム

### current_status
- カラム数: 6
- レコード数: 9

| カラム名 | データ型 |
|----------|----------|
| id | character varying |
| label | character varying |
| group_name | character varying |
| homes_id | integer |
| created_at | timestamp without time zone |
| updated_at | timestamp without time zone |

### equipment_master
- カラム数: 10
- レコード数: 14

| カラム名 | データ型 |
|----------|----------|
| id | character varying |
| item_name | character varying |
| tab_group | character varying |
| display_name | character varying |
| data_type | character varying |
| dependent_items | text |
| remarks | text |
| homes_id | integer |
| created_at | timestamp without time zone |
| updated_at | timestamp without time zone |

### floor_plan_room_types
- カラム数: 6
- レコード数: 9

| カラム名 | データ型 |
|----------|----------|
| id | character varying |
| label | character varying |
| group_name | character varying |
| homes_id | integer |
| created_at | timestamp without time zone |
| updated_at | timestamp without time zone |

### image_types
- カラム数: 6
- レコード数: 22

| カラム名 | データ型 |
|----------|----------|
| id | character varying |
| label | character varying |
| group_name | character varying |
| homes_id | integer |
| created_at | timestamp without time zone |
| updated_at | timestamp without time zone |

### land_info
- カラム数: 29
- レコード数: 0

| カラム名 | データ型 |
|----------|----------|
| id | integer |
| property_id | integer |
| postal_code | character varying |
| address_code | integer |
| prefecture | character varying |
| city | character varying |
| address | character varying |
| address_detail | character varying |
| latitude | numeric |
| longitude | numeric |

他 19 カラム

### land_rights
- カラム数: 6
- レコード数: 12

| カラム名 | データ型 |
|----------|----------|
| id | character varying |
| label | character varying |
| group_name | character varying |
| homes_id | integer |
| created_at | timestamp without time zone |
| updated_at | timestamp without time zone |

### properties
- カラム数: 44
- レコード数: 0

| カラム名 | データ型 |
|----------|----------|
| id | integer |
| company_property_number | character varying |
| external_property_id | character varying |
| property_name | character varying |
| property_name_kana | character varying |
| property_name_public | boolean |
| property_type | USER-DEFINED |
| investment_property | USER-DEFINED |
| sales_status | USER-DEFINED |
| publication_status | USER-DEFINED |

他 34 カラム

### property_equipment
- カラム数: 6
- レコード数: 0

| カラム名 | データ型 |
|----------|----------|
| id | bigint |
| property_id | bigint |
| equipment_id | character varying |
| value | character varying |
| created_at | timestamp without time zone |
| updated_at | timestamp without time zone |

### property_images
- カラム数: 11
- レコード数: 0

| カラム名 | データ型 |
|----------|----------|
| id | integer |
| property_id | integer |
| image_type | USER-DEFINED |
| file_path | character varying |
| file_url | character varying |
| display_order | integer |
| caption | text |
| is_public | boolean |
| uploaded_at | timestamp without time zone |
| created_at | timestamp without time zone |

他 1 カラム

### property_types
- カラム数: 6
- レコード数: 14

| カラム名 | データ型 |
|----------|----------|
| id | character varying |
| label | character varying |
| group_name | character varying |
| homes_id | integer |
| created_at | timestamp without time zone |
| updated_at | timestamp without time zone |

### zoning_districts
- カラム数: 6
- レコード数: 14

| カラム名 | データ型 |
|----------|----------|
| id | character varying |
| label | character varying |
| group_name | character varying |
| homes_id | integer |
| created_at | timestamp without time zone |
| updated_at | timestamp without time zone |
