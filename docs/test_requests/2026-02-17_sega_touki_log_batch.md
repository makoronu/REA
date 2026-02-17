# テスト依頼書: Seg A - touki.py ログ追加 + N+1解消

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| rea-api/app/api/api_v1/endpoints/touki.py | ステップ別ログ追加、N+1→バッチ化 |

---

## 変更概要

1. `create_property_from_touki()`: 登記レコード取得をIN句バッチ化 + ステップ別ログ
2. `apply_touki_to_property()`: 登記レコード取得・論理削除をIN句バッチ化 + ステップ別ログ

---

## テストケース

### 正常系

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | 登記→物件作成（土地+建物） | 土地1件+建物1件の登記レコードから物件作成 | 物件・land_info・building_info作成。ログに全ステップ出力 |
| 2 | 登記→物件作成（土地のみ） | 土地1件のみ | 物件・land_info作成。building_infoなし |
| 3 | 登記→物件作成（建物のみ） | 建物1件のみ | 物件・building_info作成。land_infoなし |
| 4 | 登記→既存物件反映 | 既存物件に土地+建物の登記を反映 | remarks追記、land_info更新、building_info更新 |
| 5 | 登記→既存物件反映（land_info新規） | land_infoが未作成の物件 | land_info新規作成 |
| 6 | 登記→既存物件反映（building_info新規） | building_infoが未作成の物件 | building_info新規作成 |
| 7 | 複数登記レコード（3件以上） | 土地2件+建物1件を一度に反映 | 全件バッチ取得。ログに件数出力 |

### 異常系

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 8 | 存在しない登記レコードID | 存在しないIDを含めて送信 | ResourceNotFound（404）エラー |
| 9 | 存在しない物件ID（apply） | apply-to-propertyで存在しないproperty_id | ResourceNotFound（404）エラー |
| 10 | 空の登記レコードID配列 | 空配列で送信 | ValidationError（400）エラー |
| 11 | 混合（存在+不存在） | 有効ID1件+無効ID1件 | ResourceNotFound。有効IDの処理もロールバック |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 12 | SQLインジェクション | record_idsに文字列を混入 → Pydantic型チェックで弾かれること |
| 13 | 大量ID | 100件のIDを送信 → IN句が正しく生成されること |
| 14 | 重複ID | 同じIDを2回含める → エラーにならないこと |

---

## ログ確認

テスト後、APIログに以下が出力されていること：

```
INFO: create_property_from_touki: record_ids=[...]
INFO: create_property_from_touki: property created id=XXX, type=...
INFO: create_property_from_touki: land_info created for property_id=XXX
INFO: create_property_from_touki: building_info created for property_id=XXX
INFO: create_property_from_touki: completed property_id=XXX, land=N, building=N

INFO: apply_touki_to_property: property_id=XXX, record_ids=[...]
INFO: apply_touki_to_property: remarks updated for property_id=XXX
INFO: apply_touki_to_property: land_info updated/created for property_id=XXX
INFO: apply_touki_to_property: building_info updated/created for property_id=XXX
INFO: apply_touki_to_property: N touki_records soft-deleted
INFO: apply_touki_to_property: completed property_id=XXX, land=N, building=N
```

---

## テスト環境

- API: `cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005`
- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
