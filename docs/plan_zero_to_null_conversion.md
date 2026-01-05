# 0 → NULL 変換計画

**作成日**: 2026-01-04
**対象**: 公開前確認ステータス（92件）の数値カラム

---

## 概要

ZOHOインポート時に空値が0に変換された。これによりバリデーションが「値あり」と誤判定し、必須項目チェックが機能しない。

**解決策**: NOT NULL制約を削除 → 0をNULLに変換

---

## 影響分析

### 対象レコード数
- 公開前確認: **92件**
- 非公開: 2,278件（今回は対象外）

### テーブル別の0値カウント

#### properties（17カラム）

| カラム | 0件数 | 用途 | 0が有効か |
|--------|-------|------|----------|
| priority_score | 92 | 優先度 | △ |
| sale_price | 0 | 販売価格 | ✕ |
| price_per_tsubo | 92 | 坪単価 | ✕ |
| yield_rate | 92 | 表面利回り | △ |
| current_yield | 92 | 現況利回り | △ |
| management_fee | 92 | 管理費 | △ |
| repair_reserve_fund | 92 | 修繕積立金 | △ |
| repair_reserve_fund_base | 92 | 修繕積立基金 | △ |
| parking_fee | 92 | 駐車場費 | △ |
| housing_insurance | 92 | 住宅保険 | △ |
| brokerage_fee | 92 | 仲介手数料 | △ |
| commission_split_ratio | 92 | 手数料分配率 | △ |
| current_status | 0 | 現況FK | ✕ |
| transaction_type | 0 | 取引形態FK | ✕ |
| delivery_timing | 2 | 引渡時期FK | △ |
| price_status | 0 | 価格状態FK | ✕ |
| tax_type | 0 | 税区分FK | ✕ |

#### land_info（6カラム）

| カラム | 0件数 | 用途 | 0が有効か |
|--------|-------|------|----------|
| land_area | 2 | 土地面積 | ✕ |
| building_coverage_ratio | 18 | 建ぺい率 | ✕ |
| floor_area_ratio | 18 | 容積率 | ✕ |
| land_rent | 92 | 地代 | ○（借地でない場合） |
| private_road_area | 92 | 私道面積 | ○ |
| setback_amount | 92 | セットバック | ○ |

#### building_info（21カラム）

| カラム | 0件数 | 用途 | 0が有効か |
|--------|-------|------|----------|
| building_floors_above | 33 | 地上階数 | ✕ |
| building_floors_below | 89 | 地下階数 | ○ |
| total_units | 92 | 総戸数 | ✕ |
| total_site_area | 92 | 敷地面積 | ✕ |
| building_area | 32 | 建築面積 | ✕ |
| total_floor_area | 92 | 延床面積 | ✕ |
| exclusive_area | 92 | 専有面積 | ✕ |
| balcony_area | 92 | バルコニー面積 | ○ |
| room_floor | 92 | 所在階 | ✕ |
| room_count | 92 | 部屋数 | ✕ |
| parking_capacity | 92 | 駐車場台数 | ○ |
| parking_distance | 92 | 駐車場距離 | △ |
| building_structure | 39 | 構造FK | ✕ |
| direction | 4 | 方角FK | ✕ |
| room_type | 46 | 間取りFK | ✕ |
| parking_availability | 52 | 駐車場有無FK | ✕ |
| parking_type | 92 | 駐車場種別FK | △ |
| area_measurement_type | 92 | 面積計測FK | ✕ |
| building_manager | 92 | 管理人FK | ✕ |
| management_type | 92 | 管理形態FK | ✕ |
| management_association | 92 | 管理組合FK | ✕ |

**凡例**: ○=0が有効, △=0が有効な場合あり, ✕=0は無効（NULLであるべき）

---

## 変換方針

### Phase 1: NOT NULL制約を削除

対象: DEFAULT 0 NOT NULLのカラムすべて

### Phase 2: 0 → NULL変換

**対象**: 公開前確認ステータスの物件のみ（92件）

**除外カラム**（0が意味を持つ）:
- building_floors_below（地下0階は有効）
- balcony_area（バルコニーなし=0は有効）
- parking_capacity（駐車場なし=0は有効）
- private_road_area（私道なし=0は有効）
- setback_amount（セットバックなし=0は有効）
- land_rent（借地でない=0は有効）

---

## 実行計画

### Step 1: バックアップ
```bash
pg_dump -h localhost -U rea_user -d real_estate_db > backup_before_null_conversion.sql
```

### Step 2: NOT NULL制約削除 + 0→NULL変換
SQLファイル: `scripts/migrations/convert_zero_to_null.sql`

### Step 3: 検証
- 変換後の件数確認
- バリデーションAPI動作確認

### Step 4: 本番適用
- 本番DBバックアップ
- SQL実行
- 動作確認

---

## ロールバック

```sql
-- NULL → 0に戻す
UPDATE properties SET <column> = 0 WHERE <column> IS NULL AND publication_status = '公開前確認';
-- NOT NULL制約を再追加
ALTER TABLE <table> ALTER COLUMN <column> SET NOT NULL;
```

---

## リスク

1. **フロント表示**: NULL表示が「-」や空欄になる（現状0表示よりマシ）
2. **計算処理**: COALESCE(column, 0)で対応必要な箇所があるかも
3. **ZOHO同期**: 再インポート時に再発する可能性 → インポート処理の修正が必要

---

## 次のステップ

1. この計画を承認
2. `convert_zero_to_null.sql` 作成
3. ローカルで実行・検証
4. 本番デプロイ
