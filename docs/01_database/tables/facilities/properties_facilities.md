# 🏫 properties_facilities テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `properties_facilities`
- **機能グループ**: 周辺施設
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **カラム数**: 18

## 🎯 テーブルの役割
物件周辺の施設情報を管理。学校・病院・商業施設等への距離・アクセス情報を格納。

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
| 1 | `id` | INTEGER | ❌ | nextval('properties_... | レコード識別ID | プライマリーキー |
| 2 | `property_id` | INTEGER | ❌ | - | レコード識別ID | 外部キー |
| 3 | `elementary_school_name` | VARCHAR | ✅ | - | 名称 |  |
| 4 | `elementary_school_distance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 5 | `junior_high_school_name` | VARCHAR | ✅ | - | 名称 |  |
| 6 | `junior_high_school_distance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 7 | `convenience_store_distance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 8 | `supermarket_distance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 9 | `general_hospital_distance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 10 | `facilities_conditions` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 11 | `shopping_street_distance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 12 | `drugstore_distance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 13 | `park_distance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 14 | `bank_distance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 15 | `other_facility_name` | VARCHAR | ✅ | - | 名称 |  |
| 16 | `other_facility_distance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 17 | `created_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 作成日時 | 自動設定 |
| 18 | `updated_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 日付 | 自動更新 |

## 🔗 制約・インデックス情報

### 外部キー制約
- **properties_facilities_property_id_fkey**: `property_id` → `properties_original_backup.id`

### インデックス
- **idx_properties_facilities_created_at** (INDEX): `created_at`
- **idx_properties_facilities_property_id** (INDEX): `property_id`

## 💾 使用例

### 基本操作
```sql
SELECT * FROM properties_facilities WHERE property_id = 12345;
```

## 📈 パフォーマンス情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **平均レコードサイズ**: 32768bytes
- **状況**: 小規模データのため高速アクセス可能

## 🔌 API連携情報

### API使用例
```bash
# properties_facilities データ取得
curl http://localhost:8005/api/v1/facilities/
```
