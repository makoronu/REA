# 🏢 properties テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `properties`
- **機能グループ**: 基本情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.01MB
- **カラム数**: 12

## 🎯 テーブルの役割
物件の核となる基本情報を管理。他の全ての機能テーブルの基点となる重要なテーブル。

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
| 1 | `id` | INTEGER | ✅ | - | プライマリーキー（自動採番） | プライマリーキー |
| 2 | `homes_record_id` | VARCHAR(50) | ✅ | - | ホームズシステムの物件ID | ホームズ連携用 |
| 3 | `company_property_number` | VARCHAR(500) | ✅ | - | 社内で管理する物件の一意識別番号 |  |
| 4 | `building_property_name` | VARCHAR(500) | ✅ | - | 建物名と物件名の組み合わせ |  |
| 5 | `property_name_public` | VARCHAR(3) | ✅ | - | 物件名を公開するかどうかのフラグ |  |
| 6 | `created_at` | TIMESTAMP | ✅ | - | レコードの作成日時 | 自動設定 |
| 7 | `updated_at` | TIMESTAMP | ✅ | - | レコードの最終更新日時 | 自動更新 |
| 8 | `building_structure_id` | VARCHAR(20) | ✅ | - | building_structureテーブルへの外部キー |  |
| 9 | `current_status_id` | VARCHAR(30) | ✅ | - | current_statusテーブルへの外部キー |  |
| 10 | `property_type_id` | VARCHAR(40) | ✅ | - | property_typesテーブルへの外部キー |  |
| 11 | `zoning_district_id` | VARCHAR(40) | ✅ | - | zoning_districtsテーブルへの外部キー |  |
| 12 | `land_rights_id` | VARCHAR(30) | ✅ | - | land_rightsテーブルへの外部キー |  |

## 🔗 制約・インデックス情報

## 💾 使用例

### 基本検索
```sql
SELECT * FROM properties WHERE id = 12345;
```

### 一覧取得
```sql
SELECT id, building_property_name FROM properties ORDER BY id;
```

## 📈 パフォーマンス情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.01MB
- **平均レコードサイズ**: 8192bytes
- **状況**: 小規模データのため高速アクセス可能

## 🔌 API連携情報
### 関連APIエンドポイント
- `GET /api/v1/properties/` - 物件一覧取得
- `POST /api/v1/properties/` - 物件作成
- `GET /api/v1/properties/{id}` - 物件詳細取得

### API使用例
```bash
# properties データ取得
curl http://localhost:8005/api/v1/core/
```
