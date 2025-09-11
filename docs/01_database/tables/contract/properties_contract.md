# 📋 properties_contract テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `properties_contract`
- **機能グループ**: 契約情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **カラム数**: 23

## 🎯 テーブルの役割
契約・取引に関する情報を管理。契約条件・入居時期・仲介手数料等の取引条件を格納。

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
| 1 | `id` | INTEGER | ❌ | nextval('properties_... | レコード識別ID | プライマリーキー |
| 2 | `property_id` | INTEGER | ❌ | - | レコード識別ID | 外部キー |
| 3 | `contract_period_years` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 4 | `contract_period_months` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 5 | `contract_period_type` | TEXT | ✅ | - | 種別・タイプ |  |
| 6 | `move_in_timing` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 7 | `move_in_date` | DATE | ✅ | - | 日付 |  |
| 8 | `move_in_period` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 9 | `property_manager_name` | VARCHAR | ✅ | - | 名称 |  |
| 10 | `transaction_type` | VARCHAR | ✅ | - | 種別・タイプ |  |
| 11 | `listing_confirmation_date` | VARCHAR | ✅ | - | 日付 |  |
| 12 | `tenant_placement` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 13 | `brokerage_contract_date` | DATE | ✅ | - | 日付 |  |
| 14 | `move_in_consultation` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 15 | `contract_type` | TEXT | ✅ | - | 種別・タイプ |  |
| 16 | `property_publication_type` | TEXT | ✅ | - | 種別・タイプ |  |
| 17 | `contractor_company_name` | VARCHAR | ✅ | - | 名称 |  |
| 18 | `contractor_contact_person` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 19 | `contractor_phone` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 20 | `contractor_email` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 21 | `contractor_license_number` | VARCHAR | ✅ | - | 詳細説明は準備中 |  |
| 22 | `created_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 作成日時 | 自動設定 |
| 23 | `updated_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 日付 | 自動更新 |

## 🔗 制約・インデックス情報

### 外部キー制約
- **properties_contract_property_id_fkey**: `property_id` → `properties_original_backup.id`

### インデックス
- **idx_properties_contract_created_at** (INDEX): `created_at`
- **idx_properties_contract_property_id** (INDEX): `property_id`

## 💾 使用例

### 基本操作
```sql
SELECT * FROM properties_contract WHERE property_id = 12345;
```

## 📈 パフォーマンス情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.03MB
- **平均レコードサイズ**: 32768bytes
- **状況**: 小規模データのため高速アクセス可能

## 🔌 API連携情報

### API使用例
```bash
# properties_contract データ取得
curl http://localhost:8005/api/v1/contract/
```
