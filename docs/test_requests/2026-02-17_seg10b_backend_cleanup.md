# テスト依頼書: Seg 10b - バックエンド ハードコード排除 + 未使用コード削除

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| properties.py | 公開ステータス文字列3箇所をモジュールレベル定数に置換 |
| constants.ts | 未使用エクスポート4件削除（ACTIVE/INACTIVE_SALES_STATUSES, WALK_SPEED_M_PER_MIN, TAB_INFO） |
| constants/tables.ts | 未使用エクスポート2件削除（PROPERTY_TABLES, PropertyTable） |
| shared/utils/date_format.py | ファイル削除（import先ゼロ） |

---

## 変更概要

バックエンドproperties.pyの公開ステータスハードコード文字列3箇所をモジュールレベル定数に置換。フロントエンドの未使用エクスポート6件を削除。未使用のshared/utils/date_format.pyを削除。

---

## テストケース

### 正常系

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | 物件更新 | 既存物件を編集→保存 | 正常に保存される |
| 2 | 販売ステータス→公開前確認連動 | 販売中の物件を販売準備に変更→保存 | 公開ステータスが「公開前確認」に変更 |
| 3 | 販売ステータス→非公開連動 | 販売中の物件を成約済みに変更→保存 | 公開ステータスが「非公開」に変更 |
| 4 | 不正公開ステータス拒否 | API直接: publication_status="テスト"で更新 | 400エラー |
| 5 | フロント正常動作 | 物件一覧・編集・コマンドパレット | 正常表示（削除したエクスポートの影響なし） |
| 6 | TypeScript | ビルドエラーなし（tsc --noEmit通過済み） |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 7 | レグレッション（連動） | sales_status変更時のpublication_status連動が正常動作すること |
| 8 | レグレッション（バリデーション） | 有効な公開ステータス4値が全て受け入れられること |
| 9 | 未使用コード確認 | 削除した6エクスポートがどこからもimportされていないこと（Grep確認済み） |

---

## テスト環境

- API: `cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005`
- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
