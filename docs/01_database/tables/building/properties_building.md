# 🏗️ properties_building テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `properties_building`
- **機能グループ**: 建物情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **カラム数**: 37

## 🎯 テーブルの役割
建物の構造・仕様情報を管理。建築年・構造・階数・管理情報等の建物固有のデータを格納。

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
| 1 | `id` | INTEGER | ❌ | nextval('properties_... | レコード識別ID | プライマリーキー |
| 2 | `property_id` | INTEGER | ❌ | - | レコード識別ID | 外部キー |
| 3 | `total_units` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 4 | `vacant_units` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 5 | `vacant_units_detail` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 6 | `lot_area` | NUMERIC | ✅ | - | 詳細説明は準備中 |  |
| 7 | `private_road_area` | NUMERIC | ✅ | - | 詳細説明は準備中 |  |
| 8 | `building_coverage_ratio` | NUMERIC | ✅ | - | 詳細説明は準備中 |  |
| 9 | `building_structure` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 10 | `building_area_measurement` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 11 | `building_exclusive_area` | NUMERIC | ✅ | - | 詳細説明は準備中 |  |
| 12 | `total_site_area` | NUMERIC | ✅ | - | 詳細説明は準備中 |  |
| 13 | `total_floor_area` | NUMERIC | ✅ | - | 詳細説明は準備中 |  |
| 14 | `building_area` | NUMERIC | ✅ | - | 詳細説明は準備中 |  |
| 15 | `building_floors_above` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 16 | `building_floors_below` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 17 | `construction_date` | DATE | ✅ | - | 日付 |  |
| 18 | `building_manager` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 19 | `management_type` | VARCHAR | ✅ | - | 種別・タイプ |  |
| 20 | `management_association` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 21 | `management_company` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 22 | `room_floor` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 23 | `balcony_area` | NUMERIC | ✅ | - | 詳細説明は準備中 |  |
| 24 | `direction` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 25 | `room_count` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 26 | `room_type` | TEXT | ✅ | - | 種別・タイプ |  |
| 27 | `common_management_fee` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 28 | `common_management_fee_tax` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 29 | `parking_fee` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 30 | `parking_fee_tax` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 31 | `parking_type` | TEXT | ✅ | - | 種別・タイプ |  |
| 32 | `parking_distance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 33 | `parking_available` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 34 | `parking_notes` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 35 | `renovation_common_area` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 36 | `created_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 作成日時 | 自動設定 |
| 37 | `updated_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 日付 | 自動更新 |

## 🔗 制約・インデックス情報

### 外部キー制約
- **properties_building_property_id_fkey**: `property_id` → `properties_original_backup.id`

### インデックス
- **idx_properties_building_created_at** (INDEX): `created_at`
- **idx_properties_building_property_id** (INDEX): `property_id`

## 💾 使用例

### 基本操作
```sql
SELECT * FROM properties_building WHERE property_id = 12345;
```

## 📈 パフォーマンス情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **平均レコードサイズ**: 32768bytes
- **状況**: 小規模データのため高速アクセス可能

## 🔌 API連携情報

### API使用例
```bash
# properties_building データ取得
curl http://localhost:8005/api/v1/building/
```
