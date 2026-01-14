# テスト依頼書: 用途区分フィールドの表示制御

## 作成日
2026-01-14

## 概要
土地/駐車場/その他の物件で「居住用/事業用/投資用」フィールドを非表示にし、バリデーションを除外

---

## 変更内容

| 対象 | 変更内容 |
|------|---------|
| column_labels | visible_for を建物系8種に限定 |

---

## 技術的変更点

- `is_residential`, `is_commercial`, `is_investment` の `visible_for` を設定
- 対象種別: office, warehouse, factory, store, apartment, mansion, detached, building
- 除外種別: land, parking, other

---

## テスト項目

### 正常系

| # | テスト内容 | 期待結果 | 確認 |
|---|----------|---------|------|
| 1 | 土地物件を編集画面で開く | 「居住用/事業用/投資用」が非表示 | [ ] |
| 2 | 土地物件で公開バリデーション | 用途区分エラーなし | [ ] |
| 3 | マンション物件を編集画面で開く | 「居住用/事業用/投資用」が表示される | [ ] |
| 4 | マンション物件で公開バリデーション（未選択時） | 用途区分エラーあり | [ ] |

### 異常系（リグレッション）

| # | テスト内容 | 期待結果 | 確認 |
|---|----------|---------|------|
| 5 | 駐車場物件を編集画面で開く | 「居住用/事業用/投資用」が非表示 | [ ] |
| 6 | 一戸建て物件を編集画面で開く | 「居住用/事業用/投資用」が表示される | [ ] |

---

## テスト環境

- URL: https://realestateautomation.net/

## 備考

- DB変更のみ、コード変更なし
- ロールバック: `UPDATE column_labels SET visible_for = NULL WHERE column_name IN ('is_residential', 'is_commercial', 'is_investment');`
