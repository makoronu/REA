# テスト依頼書: Seg 4/5 - エラー表示改善・コード品質修正

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| rea-admin/src/components/form/DynamicForm.tsx | バリデーションAPIエラー時にユーザー通知追加 |
| rea-admin/src/components/form/FieldFactory.tsx | console.logデバッグ文10箇所削除 |
| rea-admin/src/hooks/useMetadataForm.ts | フォームバリデーションエラーalert追加+console.log削除 |
| rea-admin/src/pages/Import/ToukiImportPage.tsx | 一括削除にtry/catch追加（部分失敗対応） |
| rea-admin/src/pages/Properties/PropertyEditDynamicPage.tsx | setTimeout 3000→MESSAGE_TIMEOUT_MS定数化 |
| rea-api/app/api/api_v1/endpoints/auth.py | タイムゾーン判定安全化（括弧追加） |

---

## 変更概要

エラー表示改善6件・コード品質修正2件。バリデーションAPI失敗時のUI通知、フォームバリデーションエラーalert、登記一括削除の部分失敗対応、ハードコード定数化、デバッグconsole.log削除、認証トークンのタイムゾーン安全判定。

---

## テストケース

### 正常系

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | 物件保存成功メッセージ | 物件編集→値変更→保存 | 「保存しました」表示後3秒で消える |
| 2 | 用途地域自動取得 | 法令調査→用途地域ボタン | 正常に取得・設定される（console.logなし） |
| 3 | 都市計画区域自動取得 | 法令調査→都市計画区域ボタン | 正常に取得・設定される |
| 4 | 住所→座標ジオコード | 住所入力済み・座標なし→用途地域ボタン | 座標取得後に用途地域取得 |
| 5 | 登記インポート正常 | 登記CSV取込→選択→一括登録 | 物件登録成功＋一時データ削除 |
| 6 | パスワードリセット | パスワードリセット→有効トークンで確認 | 正常にパスワード更新 |
| 7 | トークン有効性確認 | GET /password-reset/verify/{token} | valid: true 返却 |

### 異常系・境界値

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 8 | バリデーションAPI失敗 | ネットワーク切断→公開前確認ステータスで物件開く | 「バリデーションチェックに失敗しました」エラー表示 |
| 9 | フォームバリデーションエラー | 必須項目未入力で保存 | alertで「入力エラーがあります（X件）」表示 |
| 10 | 登記削除部分失敗 | 一括登録→削除APIが一部失敗 | 「（一時データX件の削除に失敗）」メッセージ付き成功表示 |
| 11 | 期限切れトークン | 期限切れトークンでパスワードリセット | 「トークンの有効期限が切れています」 |
| 12 | タイムゾーン付きexpires_at | DB値がタイムゾーン付きの場合 | replace()スキップ、正常比較 |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 13 | レグレッション（用途地域） | 用途地域自動取得の動作が壊れていないこと |
| 14 | レグレッション（フォーム保存） | 物件保存の通常フローが壊れていないこと |
| 15 | console.log残留 | FieldFactory.tsxのコンソール出力がないこと（DevToolsで確認） |
| 16 | TypeScript | ビルドエラーなし（tsc --noEmit通過済み） |
| 17 | Python | コンパイルエラーなし（py_compile通過済み） |

---

## テスト環境

- API: `cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005`
- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
