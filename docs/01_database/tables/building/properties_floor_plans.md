# 🏗️ properties_floor_plans テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `properties_floor_plans`
- **機能グループ**: 建物情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **カラム数**: 45

## 🎯 テーブルの役割
物件の間取り詳細情報を管理。各部屋の種類・畳数・階数等の詳細な間取りデータを格納。

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
| 1 | `id` | INTEGER | ❌ | nextval('properties_... | レコード識別ID | プライマリーキー |
| 2 | `property_id` | INTEGER | ❌ | - | レコード識別ID | 外部キー |
| 3 | `floor_plan_type_1` | TEXT | ✅ | - | 種別・タイプ |  |
| 4 | `floor_plan_tatami_1` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 5 | `floor_plan_floor_1` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 6 | `floor_plan_rooms_1` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 7 | `floor_plan_type_2` | TEXT | ✅ | - | 種別・タイプ |  |
| 8 | `floor_plan_tatami_2` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 9 | `floor_plan_floor_2` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 10 | `floor_plan_rooms_2` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 11 | `floor_plan_type_3` | TEXT | ✅ | - | 種別・タイプ |  |
| 12 | `floor_plan_tatami_3` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 13 | `floor_plan_floor_3` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 14 | `floor_plan_rooms_3` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 15 | `floor_plan_type_4` | TEXT | ✅ | - | 種別・タイプ |  |
| 16 | `floor_plan_tatami_4` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 17 | `floor_plan_floor_4` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 18 | `floor_plan_rooms_4` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 19 | `floor_plan_type_5` | TEXT | ✅ | - | 種別・タイプ |  |
| 20 | `floor_plan_tatami_5` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 21 | `floor_plan_floor_5` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 22 | `floor_plan_rooms_5` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 23 | `floor_plan_type_6` | TEXT | ✅ | - | 種別・タイプ |  |
| 24 | `floor_plan_tatami_6` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 25 | `floor_plan_floor_6` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 26 | `floor_plan_rooms_6` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 27 | `floor_plan_type_7` | TEXT | ✅ | - | 種別・タイプ |  |
| 28 | `floor_plan_tatami_7` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 29 | `floor_plan_floor_7` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 30 | `floor_plan_rooms_7` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 31 | `floor_plan_type_8` | TEXT | ✅ | - | 種別・タイプ |  |
| 32 | `floor_plan_tatami_8` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 33 | `floor_plan_floor_8` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 34 | `floor_plan_rooms_8` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 35 | `floor_plan_type_9` | TEXT | ✅ | - | 種別・タイプ |  |
| 36 | `floor_plan_tatami_9` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 37 | `floor_plan_floor_9` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 38 | `floor_plan_rooms_9` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 39 | `floor_plan_type_10` | TEXT | ✅ | - | 種別・タイプ |  |
| 40 | `floor_plan_tatami_10` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 41 | `floor_plan_floor_10` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 42 | `floor_plan_rooms_10` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 43 | `floor_plan_notes` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 44 | `created_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 作成日時 | 自動設定 |
| 45 | `updated_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 日付 | 自動更新 |

## 🔗 制約・インデックス情報

### 外部キー制約
- **properties_floor_plans_property_id_fkey**: `property_id` → `properties_original_backup.id`

### インデックス
- **idx_properties_floor_plans_created_at** (INDEX): `created_at`
- **idx_properties_floor_plans_property_id** (INDEX): `property_id`

## 💾 使用例

### 基本操作
```sql
SELECT * FROM properties_floor_plans WHERE property_id = 12345;
```

## 📈 パフォーマンス情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **平均レコードサイズ**: 32768bytes
- **状況**: 小規模データのため高速アクセス可能

## 🔌 API連携情報

### API使用例
```bash
# properties_floor_plans データ取得
curl http://localhost:8005/api/v1/building/
```
