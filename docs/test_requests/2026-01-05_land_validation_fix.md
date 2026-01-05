# テスト依頼書: 土地物件バリデーション修正

## 概要

| 項目 | 内容 |
|------|------|
| 作成日 | 2026-01-05 |
| 対象 | 土地（land）物件の公開時バリデーション |
| 変更種別 | DBデータ修正（column_labels.required_for_publication） |
| コミット | f477565 |
| 本番適用 | 済み |

---

## 変更内容

土地物件（property_type='land'）の公開時バリデーションが機能するよう、`column_labels.required_for_publication`に`land`を追加。

**追加フィールド数**: 27件
- properties: 16件
- land_info: 11件

---

## テスト対象

### 対象画面
- 物件編集画面（土地物件）
- 公開ステータス変更時のバリデーション

### 対象API
- `PUT /api/v1/properties/{id}` （公開ステータス変更時）
- `GET /api/v1/properties/{id}/validate-publication` （リアルタイムバリデーション）

---

## テストケース

### 正常系

| # | テスト内容 | 手順 | 期待結果 |
|---|-----------|------|----------|
| 1 | 土地物件で公開選択時にバリデーション発動 | 土地物件を開き、公開ステータスを「公開」に変更 | 必須項目の未入力エラーが表示される |
| 2 | 全必須項目入力後に公開可能 | 27件の必須項目をすべて入力し、公開ステータスを「公開」に変更 | エラーなく保存できる |
| 3 | 会員公開でも同様にバリデーション発動 | 土地物件で「会員公開」を選択 | 必須項目の未入力エラーが表示される |

### 異常系

| # | テスト内容 | 手順 | 期待結果 |
|---|-----------|------|----------|
| 4 | 必須項目未入力で公開不可 | 土地物件で必須項目を空のまま「公開」を選択 | 保存ボタンが無効化され、エラーモーダル表示 |
| 5 | 土地以外の物件は影響なし | マンション物件で公開ステータスを変更 | 従来通りのバリデーションが動作 |

---

## 必須項目一覧（土地物件）

### properties（16件）

| フィールド | 日本語名 |
|-----------|---------|
| property_type | 物件種別 |
| property_name | 物件名 |
| postal_code | 郵便番号 |
| prefecture | 都道府県 |
| city | 市区町村 |
| address | 町域・番地 |
| transportation | 最寄駅 |
| bus_stops | バス停 |
| nearby_facilities | 近隣施設 |
| elementary_school | 小学校 |
| junior_high_school | 中学校 |
| sale_price | 売買価格 |
| tax_type | 税込/税抜 |
| transaction_type | 取引態様 |
| current_status | 現況 |
| delivery_timing | 引渡時期 |

### land_info（11件）

| フィールド | 日本語名 |
|-----------|---------|
| use_district | 用途地域 |
| city_planning | 都市計画 |
| building_coverage_ratio | 建ぺい率 |
| floor_area_ratio | 容積率 |
| fire_prevention_district | 防火地域 |
| land_area | 土地面積 |
| land_category | 地目 |
| land_rights | 土地権利 |
| setback | セットバック |
| terrain | 地勢 |
| road_info | 接道情報 |

---

## テスト環境

| 項目 | 値 |
|------|-----|
| URL | https://realestateautomation.net/ |
| テスト用物件ID | 土地物件を1件選択（property_type='land'） |

---

## 攻撃ポイント

1. **境界値**: 必須項目のうち1つだけ未入力の場合
2. **空白値**: 空白文字のみ入力した場合（トリム処理確認）
3. **既存公開物件**: すでに「公開」状態の土地物件を編集した場合

---

## 完了条件

- [ ] テストケース1〜5すべてPASS
- [ ] 土地物件で27件の必須フィールドがチェックされることを確認
- [ ] 他の物件種別に影響がないことを確認
