# 🏞️ properties_other テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `properties_other`
- **機能グループ**: 土地・法令
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **カラム数**: 40

## 🎯 テーブルの役割
その他の物件関連情報を管理。用途地域・地勢・法的制限等の分類困難な情報を格納。

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
| 1 | `id` | INTEGER | ❌ | nextval('properties_... | レコード識別ID | プライマリーキー |
| 2 | `property_id` | INTEGER | ❌ | - | レコード識別ID | 外部キー |
| 3 | `land_category` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 4 | `use_district` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 5 | `city_planning` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 6 | `topography` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 7 | `land_area_measurement` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 8 | `private_road_ratio` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 9 | `land_ownership_ratio` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 10 | `setback` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 11 | `setback_amount` | NUMERIC | ✅ | - | 詳細説明は準備中 |  |
| 12 | `floor_area_ratio` | NUMERIC | ✅ | - | 詳細説明は準備中 |  |
| 13 | `land_rights` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 14 | `land_transaction_notice` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 15 | `legal_restrictions` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 16 | `property_features` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 17 | `notes` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 18 | `url` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 19 | `internal_memo` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 20 | `affiliated_group` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 21 | `recommendation_points` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 22 | `renovation_water` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 23 | `renovation_water_other` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 24 | `renovation_water_completion` | DATE | ✅ | - | 詳細説明は準備中 |  |
| 25 | `renovation_interior` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 26 | `renovation_interior_other` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 27 | `renovation_interior_completion` | DATE | ✅ | - | 詳細説明は準備中 |  |
| 28 | `renovation_exterior` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 29 | `renovation_exterior_other` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 30 | `renovation_exterior_completion` | DATE | ✅ | - | 詳細説明は準備中 |  |
| 31 | `renovation_common_completion` | DATE | ✅ | - | 詳細説明は準備中 |  |
| 32 | `renovation_notes` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 33 | `energy_consumption_min` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 34 | `energy_consumption_max` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 35 | `insulation_performance_min` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 36 | `insulation_performance_max` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 37 | `utility_cost_min` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 38 | `utility_cost_max` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 39 | `created_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 作成日時 | 自動設定 |
| 40 | `updated_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 日付 | 自動更新 |

## 🔗 制約・インデックス情報

### 外部キー制約
- **properties_other_property_id_fkey**: `property_id` → `properties_original_backup.id`

### インデックス
- **idx_properties_other_created_at** (INDEX): `created_at`
- **idx_properties_other_property_id** (INDEX): `property_id`

## 💾 使用例

### 基本操作
```sql
SELECT * FROM properties_other WHERE property_id = 12345;
```

## 📈 パフォーマンス情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **平均レコードサイズ**: 32768bytes
- **状況**: 小規模データのため高速アクセス可能

## 🔌 API連携情報

### API使用例
```bash
# properties_other データ取得
curl http://localhost:8005/api/v1/land/
```
