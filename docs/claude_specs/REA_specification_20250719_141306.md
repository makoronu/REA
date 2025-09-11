# 🏢 REA Project Complete Specification

**Generated**: 2025-07-19T14:13:06.029221
**Mode**: live

---

## 🚀 Overview
- **Project Name**: REA (Real Estate Automation)
- **Description**: 不動産業務完全自動化システム Python版
- **Project Path**: /Users/yaguchimakoto/my_programing/REA
- **Current Phase**: Phase 2/5 完了（スクレイピング実装済み）
- **Api Url**: http://localhost:8005
- **Github**: https://github.com/makoronu/REA

## 📁 Project Structure

**Total Files**: 116
**Total Lines**: 0

### rea-api ✅ 完成・稼働中
- Python Files: 33
- Directories: app, tests, uploads, logs, alembic

**Main Files:**
- app/main.py

**Config Files:**
- .env
- requirements.txt

### rea-scraper ✅ Mac版実装完了
- Python Files: 68
- Directories: tests, models, logs, scripts, backup, data, downloads, src

**Config Files:**
- .env
- .env.example
- requirements.txt

### rea-admin 🔄 Phase 3実装予定
- Python Files: 0
- Directories: public, src

**Config Files:**
- package.json

### rea-search ⏳ Phase 5実装予定
- Python Files: 0
- Directories: public, src

**Config Files:**
- package.json

### rea-publisher ⏳ Phase 3実装予定
- Python Files: 15
- Directories: tests, logs, src

**Config Files:**
- .env
- requirements.txt

### rea-wordpress ⏳ Phase 3実装予定
- Python Files: 0
- Directories: includes, admin, public, templates

## 📊 Database Structure

### Summary
- **Total Tables**: 12
- **Total Columns**: 386
- **Total Records**: 618
- **Total Enums**: 26

### ENUM Type Definitions
| ENUM Name | Values |
|-----------|--------|
| building_area_measurement_enum | 壁芯, 内法, 登記簿 |
| building_manager_enum | 常駐, 日勤, 巡回, 自主管理, 無 |
| contract_period_type_enum | 普通借家契約, 定期借家契約 |
| contract_type_enum | 賃貸, 売買, 賃貸・売買両方可 |
| current_status_enum | 空室, 空予定, 賃貸中, 居住中, その他 |
| designated_road_enum | 無, 有 |
| floor_plan_type_enum | R, K, DK, LDK, S ... (11 total) |
| image_type_enum | 外観, 間取図, 居室, キッチン, 風呂 ... (14 total) |
| investment_property_enum | 通常物件, 投資用物件 |
| land_area_measurement_enum | 公簿, 実測, 私測 |
| land_transaction_notice_enum | 不要, 要, 届出済 |
| management_association_enum | 無, 有 |
| move_in_period_enum | 上旬, 中旬, 下旬 |
| move_in_timing_enum | 即時, 相談, 期日指定 |
| parking_type_enum | 無, 有（無料）, 有（有料）, 近隣（無料）, 近隣（有料） |
| price_status_enum | 確定, 相談, 応相談, 変更可 |
| property_name_public_enum | 非公開, 公開 |
| property_publication_type_enum | 一般公開, 会員限定, 自社限定, 非公開 |
| road_direction_enum | 北, 北東, 東, 南東, 南 ... (8 total) |
| road_frontage_status_enum | 一方, 二方（角地）, 三方, 四方, 接道なし |
| road_type_enum | 国道, 都道府県道, 市区町村道, 私道, 位置指定道路 ... (7 total) |
| room_type_enum | 洋室, 和室, 洋和室, DK, LDK ... (9 total) |
| setback_enum | 不要, 要, セットバック済 |
| tax_enum | 税込, 税抜, 非課税 |
| tenant_placement_enum | 不可, 可 |
| topography_enum | 平坦, 高台, 低地, ひな壇, 傾斜地 ... (7 total) |

### Table Details

#### building_structure
- Columns: 6
- Records: 12

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO | ID |
| label | character varying | NO | ラベル |
| group_name | character varying | YES | グループ名 |
| homes_id | integer | YES | ホームズID |
| created_at | timestamp without time zone | YES | 作成日時 |
| updated_at | timestamp without time zone | YES | 更新日時 |

#### column_labels
- Columns: 13
- Records: 358

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| table_name | character varying | NO |  |
| column_name | character varying | NO |  |
| japanese_label | character varying | NO |  |
| description | text | YES |  |
| data_type | character varying | YES |  |
| is_required | boolean | YES |  |
| display_order | integer | YES |  |
| group_name | character varying | YES |  |
| input_type | character varying | YES |  |
| max_length | integer | YES |  |

#### current_status
- Columns: 6
- Records: 9

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO | ID |
| label | character varying | NO | ラベル |
| group_name | character varying | YES | グループ名 |
| homes_id | integer | YES | ホームズID |
| created_at | timestamp without time zone | YES | 作成日時 |
| updated_at | timestamp without time zone | YES | 更新日時 |

#### equipment_master
- Columns: 10
- Records: 116

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO | ID |
| item_name | character varying | NO | 項目名 |
| tab_group | character varying | YES | タブグループ |
| display_name | character varying | YES | 表示名 |
| data_type | character varying | YES | データ型 |
| dependent_items | text | YES | 依存項目 |
| remarks | text | YES | 備考 |
| homes_id | integer | YES | ホームズID |
| created_at | timestamp without time zone | YES | 作成日時 |
| updated_at | timestamp without time zone | YES | 更新日時 |

#### floor_plan_room_types
- Columns: 6
- Records: 9

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO | ID |
| label | character varying | NO | ラベル |
| group_name | character varying | YES | グループ名 |
| homes_id | integer | YES | ホームズID |
| created_at | timestamp without time zone | YES | 作成日時 |
| updated_at | timestamp without time zone | YES | 更新日時 |

#### image_types
- Columns: 6
- Records: 22

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO | ID |
| label | character varying | NO | ラベル |
| group_name | character varying | YES | グループ名 |
| homes_id | integer | YES | ホームズID |
| created_at | timestamp without time zone | YES | 作成日時 |
| updated_at | timestamp without time zone | YES | 更新日時 |

#### land_rights
- Columns: 6
- Records: 12

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO | ID |
| label | character varying | NO | ラベル |
| group_name | character varying | YES | グループ名 |
| homes_id | integer | YES | ホームズID |
| created_at | timestamp without time zone | YES | 作成日時 |
| updated_at | timestamp without time zone | YES | 更新日時 |

#### properties
- Columns: 304
- Records: 0

**基本情報 (12カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | integer | NO | ID |
| homes_record_id | character varying | YES | ホームズレコードID |
| company_property_number | character varying | YES | 自社管理物件番号 |
| status | character varying | YES | 状態 |
| property_type | character varying | YES | 物件種別 |
| investment_property | investment_property_enum | YES | 投資用物件 |
| building_property_name | character varying | YES | 建物名・物件名 |
| building_name_kana | character varying | YES | 建物名フリガナ(物件名フリガナ) |
| property_name_public | property_name_public_enum | YES | 物件名公開 |
| total_units | integer | YES | 総戸数・総区画数 |
| ... | (2 more columns) | ... | ... |

**所在地情報 (11カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| postal_code | character varying | YES | 郵便番号 |
| address_code | integer | YES | 所在地コード |
| address_name | character varying | YES | 所在地名称 |
| address_detail_public | text | YES | 所在地詳細_表示部 |
| address_detail_private | text | YES | 所在地詳細_非表示部 |
| latitude_longitude | character varying | YES | 緯度/経度 |
| train_line_1 | character varying | YES | 路線1 |
| station_1 | character varying | YES | 駅1 |
| bus_stop_name_1 | character varying | YES | バス停名1 |
| bus_time_1 | integer | YES | バス時間1 |
| ... | (1 more columns) | ... | ... |

**交通情報2 (6カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| train_line_2 | character varying | YES | 路線2 |
| station_2 | character varying | YES | 駅2 |
| bus_stop_name_2 | character varying | YES | バス停名2 |
| bus_time_2 | integer | YES | バス時間2 |
| walking_distance_2 | integer | YES | 徒歩距離2 |
| other_transportation | character varying | YES | その他交通 |

**土地情報 (18カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| land_category | character varying | YES | 地目 |
| use_district | character varying | YES | 用途地域 |
| city_planning | character varying | YES | 都市計画 |
| topography | topography_enum | YES | 地勢 |
| land_area_measurement | land_area_measurement_enum | YES | 土地面積計測方式 |
| lot_area | numeric | YES | 区画面積 |
| private_road_area | numeric | YES | 私道負担面積 |
| private_road_ratio | integer | YES | 私道負担割合(分子/分母) |
| land_ownership_ratio | integer | YES | 土地持分(分子/分母) |
| setback | setback_enum | YES | セットバック |
| ... | (8 more columns) | ... | ... |

**接道情報2-4 (15カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| designated_road_1 | designated_road_enum | YES | 位置指定道路1 |
| road_direction_2 | road_direction_enum | YES | 接道方向2 |
| road_frontage_width_2 | integer | YES | 接道間口2 |
| road_type_2 | road_type_enum | YES | 接道種別2 |
| road_width_2 | integer | YES | 接道幅員2 |
| designated_road_2 | designated_road_enum | YES | 位置指定道路2 |
| road_direction_3 | road_direction_enum | YES | 接道方向3 |
| road_frontage_width_3 | integer | YES | 接道間口3 |
| road_type_3 | road_type_enum | YES | 接道種別3 |
| road_width_3 | integer | YES | 接道幅員3 |
| ... | (5 more columns) | ... | ... |

**法令・権利 (5カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| designated_road_4 | designated_road_enum | YES | 位置指定道路4 |
| land_rights | integer | YES | 土地権利(借地権種類) |
| land_transaction_notice | land_transaction_notice_enum | YES | 国土法届出 |
| legal_restrictions | character varying | YES | 法令上の制限 |
| building_structure | character varying | YES | 建物構造 |

**建物情報 (13カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| building_area_measurement | building_area_measurement_enum | YES | 建物面積計測方式 |
| building_exclusive_area | numeric | YES | 建物面積・専有面積 |
| total_site_area | numeric | YES | 敷地全体面積 |
| total_floor_area | numeric | YES | 延べ床面積 |
| building_area | numeric | YES | 建築面積 |
| building_floors_above | integer | YES | 建物階数(地上) |
| building_floors_below | integer | YES | 建物階数(地下) |
| construction_date | date | YES | 築年月 |
| building_manager | building_manager_enum | YES | 管理人 |
| management_type | character varying | YES | 管理形態 |
| ... | (3 more columns) | ... | ... |

**部屋情報 (5カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| balcony_area | numeric | YES | バルコニー面積 |
| direction | road_direction_enum | YES | 向き |
| room_count | integer | YES | 間取部屋数 |
| room_type | room_type_enum | YES | 間取部屋種類 |
| floor_plan_type_1 | floor_plan_type_enum | YES | 間取(種類)1 |

**間取詳細 (40カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| floor_plan_tatami_1 | integer | YES | 間取(畳数)1 |
| floor_plan_floor_1 | integer | YES | 間取(所在階)1 |
| floor_plan_rooms_1 | integer | YES | 間取(室数)1 |
| floor_plan_type_2 | floor_plan_type_enum | YES | 間取(種類)2 |
| floor_plan_tatami_2 | integer | YES | 間取(畳数)2 |
| floor_plan_floor_2 | integer | YES | 間取(所在階)2 |
| floor_plan_rooms_2 | integer | YES | 間取(室数)2 |
| floor_plan_type_3 | floor_plan_type_enum | YES | 間取(種類)3 |
| floor_plan_tatami_3 | integer | YES | 間取(畳数)3 |
| floor_plan_floor_3 | integer | YES | 間取(所在階)3 |
| ... | (30 more columns) | ... | ... |

**物件詳細 (4カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| property_features | text | YES | 物件の特徴 |
| notes | text | YES | 備考 |
| url | character varying | YES | URL |
| internal_memo | text | YES | 社内用メモ |

**価格情報 (17カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| rent_price | integer | YES | 賃料・価格 |
| price_status | price_status_enum | YES | 価格状態 |
| tax | tax_enum | YES | 税金 |
| tax_amount | tax_enum | YES | 税額 |
| price_per_tsubo | integer | YES | 坪単価 |
| common_management_fee | integer | YES | 共益費・管理費 |
| common_management_fee_tax | tax_enum | YES | 共益費・管理費 税 |
| full_occupancy_yield | integer | YES | 満室時表面利回り |
| current_yield | integer | YES | 現行利回り |
| housing_insurance | integer | YES | 住宅保険料 |
| ... | (7 more columns) | ... | ... |

**駐車場情報 (5カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| parking_fee_tax | tax_enum | YES | 駐車場料金 税 |
| parking_type | parking_type_enum | YES | 駐車場区分 |
| parking_distance | integer | YES | 駐車場距離 |
| parking_available | integer | YES | 駐車場空き台数 |
| parking_notes | text | YES | 駐車場備考 |

**入居情報 (4カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| current_status | current_status_enum | YES | 現況 |
| move_in_timing | move_in_timing_enum | YES | 引渡/入居時期 |
| move_in_date | date | YES | 引渡/入居年月 |
| move_in_period | move_in_period_enum | YES | 引渡/入居旬 |

**周辺施設 (6カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| elementary_school_name | character varying | YES | 小学校名 |
| elementary_school_distance | integer | YES | 小学校距離 |
| junior_high_school_name | character varying | YES | 中学校名 |
| junior_high_school_distance | integer | YES | 中学校距離 |
| convenience_store_distance | integer | YES | コンビニ距離 |
| supermarket_distance | integer | YES | スーパー距離 |

**施設・契約情報 (8カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| general_hospital_distance | integer | YES | 総合病院距離 |
| property_manager_name | character varying | YES | 物件担当者名 |
| transaction_type | character varying | YES | 取引態様 |
| listing_confirmation_date | character varying | YES | 掲載確認日 |
| tenant_placement | tenant_placement_enum | YES | 客付 |
| brokerage_contract_date | date | YES | 媒介契約年月日 |
| brokerage_fee | integer | YES | 仲介手数料 |
| commission_split_ratio | numeric | YES | 分配率(客付分) |

**画像情報 (92カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| image_type_1 | image_type_enum | YES | 画像種別1 |
| image_comment_1 | text | YES | 画像コメント1 |
| local_file_name_2 | character varying | YES | ローカルファイル名2 |
| image_type_2 | image_type_enum | YES | 画像種別2 |
| image_comment_2 | text | YES | 画像コメント2 |
| local_file_name_3 | character varying | YES | ローカルファイル名3 |
| image_type_3 | image_type_enum | YES | 画像種別3 |
| image_comment_3 | text | YES | 画像コメント3 |
| local_file_name_4 | character varying | YES | ローカルファイル名4 |
| image_type_4 | image_type_enum | YES | 画像種別4 |
| ... | (82 more columns) | ... | ... |

**その他情報 (8カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| shopping_street_distance | integer | YES | 商店街距離 |
| drugstore_distance | integer | YES | ドラッグストア距離 |
| park_distance | integer | YES | 公園距離 |
| bank_distance | integer | YES | 銀行距離 |
| other_facility_name | character varying | YES | その他名 |
| other_facility_distance | integer | YES | その他距離 |
| contract_type | contract_type_enum | YES | 契約形態 |
| property_publication_type | property_publication_type_enum | YES | 物件公開区分 |

**リフォーム情報 (12カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| renovation_water | character varying | YES | リフォーム箇所（水回り） |
| renovation_water_other | character varying | YES | リフォーム箇所その他（水回り） |
| renovation_water_completion | date | YES | 施工完了年月（水回り） |
| renovation_interior | character varying | YES | リフォーム箇所（内装） |
| renovation_interior_other | character varying | YES | リフォーム箇所その他（内装） |
| renovation_interior_completion | date | YES | 施工完了年月（内装） |
| renovation_exterior | character varying | YES | リフォーム箇所（外装） |
| renovation_exterior_other | character varying | YES | リフォーム箇所その他（外装） |
| renovation_exterior_completion | date | YES | 施工完了年月（外装） |
| renovation_common_area | character varying | YES | リフォーム箇所（共用部分） |
| ... | (2 more columns) | ... | ... |

**省エネ性能 (6カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| energy_consumption_min | integer | YES | エネルギー消費性能/エネルギー消費性能(最小) |
| energy_consumption_max | integer | YES | エネルギー消費性能(最大) |
| insulation_performance_min | integer | YES | 断熱性能/断熱性能(最小) |
| insulation_performance_max | integer | YES | 断熱性能(最大) |
| utility_cost_min | integer | YES | 目安光熱費/目安光熱費(最小) |
| utility_cost_max | integer | YES | 目安光熱費(最大) |

**システム情報 (7カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| created_at | timestamp without time zone | YES | 作成日時 |
| updated_at | timestamp without time zone | YES | 更新日時 |
| building_structure_id | character varying | YES | 建物構造ID |
| current_status_id | character varying | YES | 現況ID |
| property_type_id | character varying | YES | 物件種別ID |
| zoning_district_id | character varying | YES | 用途地域ID |
| land_rights_id | character varying | YES | 土地権利ID |

**元請会社情報 (6カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| contractor_company_name | character varying | YES | 元請会社名 |
| contractor_contact_person | character varying | YES | 担当者名 |
| contractor_phone | character varying | YES | 電話番号 |
| contractor_email | character varying | YES | メールアドレス |
| contractor_address | character varying | YES | 会社住所 |
| contractor_license_number | character varying | YES | 宅建免許番号 |

**その他 (4カラム):**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| source_site | character varying | YES |  |
| extraction_confidence | double precision | YES |  |
| data_quality_score | double precision | YES |  |
| original_data | json | YES |  |

#### property_equipment
- Columns: 6
- Records: 0

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | bigint | NO | ID |
| property_id | bigint | NO | 物件ID |
| equipment_id | character varying | NO | 設備ID |
| value | character varying | YES | 値 |
| created_at | timestamp without time zone | YES | 作成日時 |
| updated_at | timestamp without time zone | YES | 更新日時 |

#### property_types
- Columns: 6
- Records: 63

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO | ID |
| label | character varying | NO | ラベル |
| group_name | character varying | YES | グループ名 |
| homes_id | integer | YES | ホームズID |
| created_at | timestamp without time zone | YES | 作成日時 |
| updated_at | timestamp without time zone | YES | 更新日時 |

#### site_master
- Columns: 11
- Records: 3

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO |  |
| site_name | character varying | NO |  |
| base_url | character varying | NO |  |
| site_type | character varying | NO |  |
| learning_status | character varying | YES |  |
| learned_patterns_count | integer | YES |  |
| overall_accuracy | double precision | YES |  |
| last_learning_date | timestamp without time zone | YES |  |
| is_active | boolean | YES |  |
| created_at | timestamp without time zone | YES |  |

#### zoning_districts
- Columns: 6
- Records: 14

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO | ID |
| label | character varying | NO | ラベル |
| group_name | character varying | YES | グループ名 |
| homes_id | integer | YES | ホームズID |
| created_at | timestamp without time zone | YES | 作成日時 |
| updated_at | timestamp without time zone | YES | 更新日時 |

## 🔌 API Specification

### Total Endpoints: 8
**Base URL**: http://localhost:8005

| Method | Path | Summary |
|--------|------|---------|
| GET | /api/v1/properties/ | 物件一覧取得 |
| POST | /api/v1/properties/ | 物件作成 |
| GET | /api/v1/properties/{property_id} | 物件詳細取得 |
| PUT | /api/v1/properties/{property_id} | 物件更新 |
| DELETE | /api/v1/properties/{property_id} | 物件削除 |
| GET | /api/v1/properties/by-contractor/{company_name} | 元請会社別物件取得 |
| GET | /api/v1/properties/contractors/contacts | 元請会社連絡先一覧 |
| GET | /health | ヘルスチェック |

## 💻 Implementation Status

### ✅ Completed

**Phase 1: データベース基盤・API**
- PostgreSQL 15 + 11テーブル
- FastAPI + 8エンドポイント
- 元請会社情報管理機能

**Phase 2: スクレイピング（Mac版）**
- ホームズ対応完了
- 段階処理システム実装
- Bot対策実装済み

### 🔄 In Progress
**Phase 3: React管理画面・自動入稿** (設計段階)

### ⏳ Planned
- Phase 4: AI機能・検索最適化
- Phase 5: 公開検索サイト

## 📝 Recent Changes

**Last Update**: 2025-07-19 14:13
**Current Branch**: main

**Recent Commits:**
- f7b828c 🎉 REA Python版プロジェクト初期化

**Total Commits**: 1

## 🛠 Development Guide

### Tech Stack

**Backend:**
- Python 3.9+
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- PostgreSQL 15
- Docker

**Scraping:**
- Selenium 4.15.2
- undetected-chromedriver 3.5.3
- BeautifulSoup4 4.12.2

**Planned:**
- React 18
- TypeScript
- Tailwind CSS

### Code Patterns
- **Api**: FastAPI + Pydantic + SQLAlchemy
- **Scraping**: 段階処理 + Bot対策
- **Error Handling**: 全体書き直し方式

### Important Notes
- Mac環境（macOS）で開発
- プロジェクトパス: /Users/yaguchimakoto/my_programing/REA
- Python仮想環境: ./venv
- ポート: API=8005, DB=5432