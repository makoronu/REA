# テストレポート: 土地物件バリデーション修正

**テスト日:** 2026-01-05
**テスター:** Claude Code (自動テスト)
**コミット:** f477565

---

## サマリー

| # | テスト内容 | 期待結果 | 実際 | 結果 |
|---|-----------|---------|------|------|
| 1 | 土地物件で公開選択→バリデーション発動 | エラー表示 | バリデーション通過 | ❌ FAIL |
| 3 | 他物件種別に影響なし | 従来通り | 3件不足表示 | ✅ PASS |
| 4 | 必須項目未入力で公開不可 | 400エラー | 200で公開成功 | ❌ FAIL |

**総合判定: ❌ FAIL (2件)**

---

## 問題発見

### ローカルDBのデータ不整合

**期待される状態（テスト依頼書より）:**
- 土地物件の必須フィールド: 27件
  - properties: 16件
  - land_info: 11件

**実際の状態（ローカルDB）:**
- 土地物件の必須フィールド: **7件のみ**
  - properties: 5件
  - land_info: 2件

### DBクエリ結果

```sql
SELECT table_name, column_name
FROM column_labels
WHERE 'land' = ANY(required_for_publication);
```

| table_name | column_name |
|------------|-------------|
| land_info | building_coverage_ratio |
| land_info | floor_area_ratio |
| properties | bus_stops |
| properties | elementary_school |
| properties | junior_high_school |
| properties | nearby_facilities |
| properties | transportation |

**不足フィールド（20件）:**

properties（11件不足）:
- property_type
- property_name
- postal_code
- prefecture
- city
- address
- sale_price
- tax_type
- transaction_type
- current_status
- delivery_timing

land_info（9件不足）:
- use_district
- city_planning
- fire_prevention_district
- land_area
- land_category
- land_rights
- setback
- terrain
- road_info

---

## テスト詳細

### テスト1: 土地物件で公開選択時にバリデーション発動

```
対象物件ID: 2480
property_type: land
publication_status: 公開（テスト前に既に公開状態）

バリデーションAPI結果:
- is_valid: True
- 不足項目: なし

判定: ❌ FAIL
```

**原因:** 土地物件に対する必須フィールド設定がDBに不足

### テスト3: 他物件種別に影響なし（一戸建て）

```
対象物件ID: 2093
property_type: house

バリデーションAPI結果:
- is_valid: False
- 不足項目: 3件

判定: ✅ PASS
```

### テスト4: 必須項目未入力で公開不可

```
PUT /api/v1/properties/2480
Body: {"publication_status": "公開"}

結果: 200 OK（公開成功）

判定: ❌ FAIL
```

**原因:** 必須フィールドが設定されていないため、バリデーションが発動しない

---

## 結論

**❌ FAIL - ローカルDBにDBマイグレーションが適用されていない**

### 根本原因

テスト依頼書に記載された `f477565` コミットで追加されたDB変更（27件のland必須フィールド追加）が、ローカルDBに適用されていない。

### 確認事項

1. DBマイグレーションスクリプトの確認
2. 本番DBとの差分確認
3. マイグレーション適用後に再テスト

---

## 次のアクション

1. 開発者にDBマイグレーション未適用を報告
2. マイグレーション適用後、再テスト実施
