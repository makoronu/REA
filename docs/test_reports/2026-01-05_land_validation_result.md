# テスト結果レポート: 土地物件バリデーション修正

## 概要

| 項目 | 内容 |
|------|------|
| 実施日 | 2026-01-05 |
| 対象 | 土地（land）物件の公開時バリデーション |
| 総合判定 | ✅ ALL PASS |

---

## テスト結果

### DBテスト

| # | テスト内容 | 期待値 | 実測値 | 結果 |
|---|-----------|--------|--------|------|
| 1 | 必須フィールド総数 | 27 | 27 | ✅ PASS |
| 2 | properties必須フィールド | 16 | 16 | ✅ PASS |
| 3 | land_info必須フィールド | 11 | 11 | ✅ PASS |
| 4 | 他物件種別への影響 | 変更なし | mansion=43件（変更なし） | ✅ PASS |
| 5 | バリデーションクエリ動作 | 正常 | 正常 | ✅ PASS |

### UIテスト（Selenium ヘッドレス）

| # | テスト内容 | 結果 |
|---|-----------|------|
| 1 | ログイン | ✅ PASS |
| 2 | 土地物件ページ表示（ID: 441） | ✅ PASS |
| 3 | スクリーンショット取得 | ✅ PASS |

---

## スクリーンショット

- `test_screenshots/land_validation_before.png`
- `test_screenshots/land_validation_after.png`

---

## 確認済み必須フィールド（土地物件）

### properties（16件）

| フィールド | 日本語名 | 状態 |
|-----------|---------|------|
| property_type | 物件種別 | ✅ |
| property_name | 物件名 | ✅ |
| postal_code | 郵便番号 | ✅ |
| prefecture | 都道府県 | ✅ |
| city | 市区町村 | ✅ |
| address | 町域・番地 | ✅ |
| transportation | 最寄駅 | ✅ |
| bus_stops | バス停 | ✅ |
| nearby_facilities | 近隣施設 | ✅ |
| elementary_school | 小学校 | ✅ |
| junior_high_school | 中学校 | ✅ |
| sale_price | 売買価格 | ✅ |
| tax_type | 税込/税抜 | ✅ |
| transaction_type | 取引態様 | ✅ |
| current_status | 現況 | ✅ |
| delivery_timing | 引渡時期 | ✅ |

### land_info（11件）

| フィールド | 日本語名 | 状態 |
|-----------|---------|------|
| use_district | 用途地域 | ✅ |
| city_planning | 都市計画 | ✅ |
| building_coverage_ratio | 建ぺい率 | ✅ |
| floor_area_ratio | 容積率 | ✅ |
| fire_prevention_district | 防火地域 | ✅ |
| land_area | 土地面積 | ✅ |
| land_category | 地目 | ✅ |
| land_rights | 土地権利 | ✅ |
| setback | セットバック | ✅ |
| terrain | 地勢 | ✅ |
| road_info | 接道情報 | ✅ |

---

## 結論

土地物件のバリデーション設定が正しく適用されていることを確認。
本番DBに27件の必須フィールドが設定済み。
