# 💰 properties_pricing テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `properties_pricing`
- **機能グループ**: 価格・収益
- **レコード数**: 0件
- **テーブルサイズ**: 0.04MB
- **カラム数**: 16

## 🎯 テーブルの役割
物件の価格・賃料・利回り等の収益に関する情報を管理。投資判断に必要な数値データが集約されている。

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
| 1 | `id` | INTEGER | ❌ | nextval('properties_... | レコード識別ID | プライマリーキー |
| 2 | `property_id` | INTEGER | ❌ | - | レコード識別ID | 外部キー |
| 3 | `price` | INTEGER | ✅ | - | 価格・賃料 | 円単位 |
| 4 | `tax` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 5 | `tax_amount` | TEXT | ✅ | - | 詳細説明は準備中 |  |
| 6 | `price_per_tsubo` | INTEGER | ✅ | - | 価格・賃料 |  |
| 7 | `full_occupancy_yield` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 8 | `current_yield` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 9 | `housing_insurance` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 10 | `land_rent` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 11 | `repair_reserve_fund` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 12 | `repair_reserve_fund_base` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 13 | `brokerage_fee` | INTEGER | ✅ | - | 詳細説明は準備中 |  |
| 14 | `commission_split_ratio` | NUMERIC | ✅ | - | 詳細説明は準備中 |  |
| 15 | `created_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 作成日時 | 自動設定 |
| 16 | `updated_at` | TIMESTAMP | ✅ | CURRENT_TIMESTAMP | 日付 | 自動更新 |

## 🔗 制約・インデックス情報

### 外部キー制約
- **properties_pricing_property_id_fkey**: `property_id` → `properties_original_backup.id`

### インデックス
- **idx_properties_pricing_created_at** (INDEX): `created_at`
- **idx_properties_pricing_price** (INDEX): `price`
- **idx_properties_pricing_property_id** (INDEX): `property_id`

## 💾 使用例

### 価格範囲検索
```sql
SELECT * FROM properties_pricing WHERE price BETWEEN 100000 AND 200000;
```

### 利回り上位
```sql
SELECT * FROM properties_pricing ORDER BY yield DESC LIMIT 10;
```

## 📈 パフォーマンス情報
- **レコード数**: 0件
- **テーブルサイズ**: 0.04MB
- **平均レコードサイズ**: 40960bytes
- **状況**: 小規模データのため高速アクセス可能

## 🔌 API連携情報
### 関連APIエンドポイント
- `GET /api/v1/properties/{id}/pricing` - 価格情報取得
- `PUT /api/v1/properties/{id}/pricing` - 価格情報更新

### API使用例
```bash
# properties_pricing データ取得
curl http://localhost:8005/api/v1/pricing/
```
