# 🏢 REA Project Complete Specification

**Generated**: 2025-07-19T07:40:27.302380
**Mode**: live

---

## 🚀 Overview
- **Project Name**: REA (Real Estate Automation)
- **Description**: 不動産業務完全自動化システム Python版
- **Project Path**: /Users/yaguchimakoto/my_programing/REA
- **Current Phase**: Phase 2/5 完了（スクレイピング実装済み）
- **Api Url**: http://localhost:8005
- **Github**: https://github.com/makoronu/REA

## 📊 Database Structure

### Summary
- **Total Tables**: 17
- **Total Columns**: 413
- **Total Records**: 1,178

### Table Details

#### building_structure
- Columns: 6
- Records: 12

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO |  |
| label | character varying | NO |  |
| group_name | character varying | YES |  |
| homes_id | integer | YES |  |
| created_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES |  |

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
| id | character varying | NO |  |
| label | character varying | NO |  |
| group_name | character varying | YES |  |
| homes_id | integer | YES |  |
| created_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES |  |

#### database_complete_structure
- Columns: 8
- Records: 413

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| table_name | name | YES |  |
| column_name | name | YES |  |
| position | integer | YES |  |
| data_type | name | YES |  |
| is_nullable | character varying | YES |  |
| column_default | character varying | YES |  |
| column_comment_jp | text | YES |  |
| constraint_info | text | YES |  |

#### equipment_master
- Columns: 10
- Records: 116

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO |  |
| item_name | character varying | NO |  |
| tab_group | character varying | YES |  |
| display_name | character varying | YES |  |
| data_type | character varying | YES |  |
| dependent_items | text | YES |  |
| remarks | text | YES |  |
| homes_id | integer | YES |  |
| created_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES |  |

#### floor_plan_room_types
- Columns: 6
- Records: 9

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO |  |
| label | character varying | NO |  |
| group_name | character varying | YES |  |
| homes_id | integer | YES |  |
| created_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES |  |

#### image_types
- Columns: 6
- Records: 22

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO |  |
| label | character varying | NO |  |
| group_name | character varying | YES |  |
| homes_id | integer | YES |  |
| created_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES |  |

#### land_rights
- Columns: 6
- Records: 12

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO |  |
| label | character varying | NO |  |
| group_name | character varying | YES |  |
| homes_id | integer | YES |  |
| created_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES |  |

#### properties
- Columns: 304
- Records: 0

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | integer | NO | ID |
| homes_record_id | character varying | YES | ホームズレコードID |
| company_property_number | character varying | YES | 自社管理物件番号 |
| status | character varying | YES | 状態 |
| property_type | character varying | YES | 物件種別 |
| investment_property | USER-DEFINED | YES | 投資用物件 |
| building_property_name | character varying | YES | 建物名・物件名 |
| building_name_kana | character varying | YES | 建物名フリガナ(物件名フリガナ) |
| property_name_public | USER-DEFINED | YES | 物件名公開 |
| total_units | integer | YES | 総戸数・総区画数 |

#### property_equipment
- Columns: 6
- Records: 0

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | bigint | NO |  |
| property_id | bigint | NO |  |
| equipment_id | character varying | NO |  |
| value | character varying | YES |  |
| created_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES |  |

#### property_types
- Columns: 6
- Records: 63

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO |  |
| label | character varying | NO |  |
| group_name | character varying | YES |  |
| homes_id | integer | YES |  |
| created_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES |  |

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

#### v_columns_by_group
- Columns: 5
- Records: 39

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| table_name | character varying | YES |  |
| group_name | character varying | YES |  |
| column_count | bigint | YES |  |
| start_order | integer | YES |  |
| end_order | integer | YES |  |

#### v_enum_columns
- Columns: 5
- Records: 78

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| table_name | character varying | YES |  |
| column_name | character varying | YES |  |
| japanese_label | character varying | YES |  |
| enum_values | text | YES |  |
| enum_count | integer | YES |  |

#### v_required_columns
- Columns: 6
- Records: 20

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| table_name | character varying | YES |  |
| column_name | character varying | YES |  |
| japanese_label | character varying | YES |  |
| data_type | character varying | YES |  |
| group_name | character varying | YES |  |
| display_order | integer | YES |  |

#### v_table_labels
- Columns: 3
- Records: 10

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| table_name | character varying | YES |  |
| column_count | bigint | YES |  |
| max_display_order | integer | YES |  |

#### zoning_districts
- Columns: 6
- Records: 14

**主要カラム:**
| Column | Type | Nullable | Japanese Label |
|--------|------|----------|----------------|
| id | character varying | NO |  |
| label | character varying | NO |  |
| group_name | character varying | YES |  |
| homes_id | integer | YES |  |
| created_at | timestamp without time zone | YES |  |
| updated_at | timestamp without time zone | YES |  |

## 🔌 API Specification

### Total Endpoints: 0
**Base URL**: http://localhost:8005

| Method | Path | Summary |
|--------|------|---------|

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

**Last Update**: 2025-07-19 07:40

**Recent Commits:**
- f7b828c 🎉 REA Python版プロジェクト初期化

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