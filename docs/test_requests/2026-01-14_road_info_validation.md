# テスト依頼書: 接道関係バリデーション修正

## 作成日
2026-01-14

## 概要
road_info（接道関係）のrequired_for_publicationを全物件種別に修正

---

## 変更内容

| 対象 | 変更内容 |
|------|---------|
| column_labels | road_info.required_for_publication を全物件種別に設定 |

---

## 技術的変更点

- `road_info.required_for_publication`
  - 変更前: `{land}`（土地のみ）
  - 変更後: `{mansion,apartment,detached,office,store,warehouse,factory,building,land}`

---

## テスト項目

### 正常系

| # | テスト内容 | 期待結果 | 確認 |
|---|----------|---------|------|
| 1 | マンション物件（接道関係未入力）で公開バリデーション | 「接道関係」エラーあり | [ ] |
| 2 | 一戸建て物件（接道関係未入力）で公開バリデーション | 「接道関係」エラーあり | [ ] |
| 3 | 土地物件（接道関係未入力）で公開バリデーション | 「接道関係」エラーあり | [ ] |
| 4 | 接道関係入力済みの物件で公開バリデーション | 「接道関係」エラーなし | [ ] |

### 異常系（リグレッション）

| # | テスト内容 | 期待結果 | 確認 |
|---|----------|---------|------|
| 5 | 接道なし（no_road_access: true）の物件で公開バリデーション | 「接道関係」エラーなし | [ ] |
| 6 | 物件編集画面の他機能 | 正常に動作 | [ ] |

---

## テスト環境

- URL: https://realestateautomation.net/

## 備考

- DB変更のみ、コード変更なし
- ロールバック: `UPDATE column_labels SET required_for_publication = '{land}' WHERE table_name = 'land_info' AND column_name = 'road_info';`
