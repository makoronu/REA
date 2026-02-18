# テスト依頼書: Seg 8b - 定数整理・ハードコード排除

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| rea-admin/src/constants.ts | PUBLICATION_STATUS拡張（+会員公開/公開前確認）、SALES_STATUS拡張（+査定中）、ZONE_COLORS追加 |
| rea-admin/src/components/form/DynamicForm.tsx | ハードコード文字列8箇所を定数参照に置換 |
| rea-admin/src/components/form/ZoningMapField.tsx | ローカルZONE_COLORS削除→constants.tsからimport |
| rea-admin/src/pages/ZoningMap/ZoningMapPage.tsx | ローカルZONE_COLORS削除→constants.tsからimport |

---

## 変更概要

フロントエンド定数整理。PUBLICATION_STATUS/SALES_STATUSの不足値追加、DynamicForm.tsxの全ハードコードステータス文字列を定数参照に置換、ZONE_COLORSの2ファイル重複定義をconstants.tsに一元化。動作変更なし（リファクタリング）。

---

## テストケース

### 正常系

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | 物件編集画面表示 | 物件一覧→物件編集 | 正常に表示される |
| 2 | 公開ステータス変更 | 公開ステータスボタンで「公開」選択 | バリデーション実行→結果に応じて公開/公開前確認に設定 |
| 3 | 非公開→公開前確認 | バリデーションエラー時 | 「公開前確認」に自動設定される |
| 4 | 公開前確認物件表示 | 公開前確認ステータスの物件を開く | 初期バリデーションが実行される |
| 5 | 販売中→公開可能 | 販売中の物件で公開ステータス変更 | 公開/会員公開ボタンが有効 |
| 6 | 査定中→公開不可 | 査定中の物件で公開ステータス確認 | 非公開以外のボタンが無効 |
| 7 | 用途地域マップ（Field） | 法令調査タブ→用途地域マップ | 正常に色分け表示 |
| 8 | 用途地域マップ（Page） | サイドバー→用途地域マップ | 正常に色分け表示 |
| 9 | 物件保存 | 物件編集→保存 | 正常に保存される |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 10 | レグレッション（ステータス連動） | 販売ステータス→公開ステータスの連動が壊れていないこと |
| 11 | レグレッション（バリデーション） | 公開バリデーションが正常に動作すること |
| 12 | レグレッション（マップ色） | 用途地域の色分けが両画面で同一であること |
| 13 | TypeScript | ビルドエラーなし（tsc --noEmit通過済み） |

---

## テスト環境

- API: `cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005`
- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
