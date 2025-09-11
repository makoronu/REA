# 📍 properties_transportation テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `properties_transportation`
- **機能グループ**: 所在地・交通
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **カラム数**: 15

## 🎯 テーブルの役割
物件の交通アクセス情報を管理。最寄り駅・路線・徒歩時間・バス情報等を格納。

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
| 1 | `id` | INTEGER | ❌ | nextval('properties_... | レコード識別ID | プライマリーキー |
| 2 | `property_id` | INTEGER | ❌ | - | レコード識別ID | 外部キー |
| 3 | `train_line_1` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 4 | `station_1` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 5 | `bus_stop_name_1` | VARCHAR | ✅ | - | 名称 |  |
| 6 | `bus_time_1` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 7 | `walking_distance_1` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 8 | `train_line_2` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 9 | `station_2` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 10 | `bus_stop_name_2` | VARCHAR | ✅ | - | 名称 |  |
| 11 | `bus_time_2` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 12 | `walking_distance_2` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 13 | `other_transportation` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 14 | `created_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 作成日時 | 自動設定 |
| 15 | `updated_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 日付 | 自動更新 |

## 🔗 制約・インデックス情報

### 外部キー制約
- **properties_transportation_property_id_fkey**: `property_id` → `properties_original_backup.id`

### インデックス
- **idx_properties_transportation_created_at** (INDEX): `created_at`
- **idx_properties_transportation_property_id** (INDEX): `property_id`

## 💾 使用例

### 基本操作
```sql
SELECT * FROM properties_transportation WHERE property_id = 12345;
```

## 📈 パフォーマンス情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **平均レコードサイズ**: 32768bytes
- **状況**: 小規模データのため高速アクセス可能

## 🔌 API連携情報

### API使用例
```bash
# properties_transportation データ取得
curl http://localhost:8005/api/v1/location/
```
