# 📍 properties_location テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `properties_location`
- **機能グループ**: 所在地・交通
- **レコード数**: 0件
- **テーブルサイズ**: 0.04MB
- **カラム数**: 11

## 🎯 テーブルの役割
物件の住所・所在地情報を管理。郵便番号・住所・緯度経度等の位置特定に必要なデータを格納。

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
| 1 | `id` | INTEGER | ❌ | nextval('properties_... | レコード識別ID | プライマリーキー |
| 2 | `property_id` | INTEGER | ❌ | - | レコード識別ID | 外部キー |
| 3 | `postal_code` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 4 | `address_code` | INTEGER | ✅ | - | 住所 |  |
| 5 | `address_name` | VARCHAR | ✅ | - | 住所 |  |
| 6 | `address_detail_public` | TEXT | ✅ | - | 住所 |  |
| 7 | `address_detail_private` | TEXT | ✅ | - | 住所 |  |
| 8 | `latitude_longitude` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 9 | `contractor_address` | VARCHAR | ✅ | - | 住所 |  |
| 10 | `created_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 作成日時 | 自動設定 |
| 11 | `updated_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 日付 | 自動更新 |

## 🔗 制約・インデックス情報

### 外部キー制約
- **properties_location_property_id_fkey**: `property_id` → `properties_original_backup.id`

### インデックス
- **idx_properties_location_created_at** (INDEX): `created_at`
- **idx_properties_location_postal_code** (INDEX): `postal_code`
- **idx_properties_location_property_id** (INDEX): `property_id`

## 💾 使用例

### 基本操作
```sql
SELECT * FROM properties_location WHERE property_id = 12345;
```

## 📈 パフォーマンス情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.04MB
- **平均レコードサイズ**: 40960bytes
- **状況**: 小規模データのため高速アクセス可能

## 🔌 API連携情報

### API使用例
```bash
# properties_location データ取得
curl http://localhost:8005/api/v1/location/
```
