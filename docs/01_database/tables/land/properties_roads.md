# 🏞️ properties_roads テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `properties_roads`
- **機能グループ**: 土地・法令
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **カラム数**: 16

## 🎯 テーブルの役割
物件の接道情報を管理。道路の方向・幅員・種別等の法的要件に関わる重要なデータを格納。

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
| 1 | `id` | INTEGER | ❌ | nextval('properties_... | レコード識別ID | プライマリーキー |
| 2 | `property_id` | INTEGER | ❌ | - | レコード識別ID | 外部キー |
| 3 | `road_direction_1` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 4 | `road_type_1` | TEXT | ✅ | - | 種別・タイプ |  |
| 5 | `designated_road_1` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 6 | `road_direction_2` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 7 | `road_type_2` | TEXT | ✅ | - | 種別・タイプ |  |
| 8 | `designated_road_2` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 9 | `road_direction_3` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 10 | `road_type_3` | TEXT | ✅ | - | 種別・タイプ |  |
| 11 | `designated_road_3` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 12 | `road_direction_4` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 13 | `road_type_4` | TEXT | ✅ | - | 種別・タイプ |  |
| 14 | `designated_road_4` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 15 | `created_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 作成日時 | 自動設定 |
| 16 | `updated_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 日付 | 自動更新 |

## 🔗 制約・インデックス情報

### 外部キー制約
- **properties_roads_property_id_fkey**: `property_id` → `properties_original_backup.id`

### インデックス
- **idx_properties_roads_created_at** (INDEX): `created_at`
- **idx_properties_roads_property_id** (INDEX): `property_id`

## 💾 使用例

### 基本操作
```sql
SELECT * FROM properties_roads WHERE property_id = 12345;
```

## 📈 パフォーマンス情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **平均レコードサイズ**: 32768bytes
- **状況**: 小規模データのため高速アクセス可能

## 🔌 API連携情報

### API使用例
```bash
# properties_roads データ取得
curl http://localhost:8005/api/v1/land/
```
