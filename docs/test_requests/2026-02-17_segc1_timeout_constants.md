# テスト依頼書: Seg C-1 - タイムアウト定数集約

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| rea-admin/src/constants.ts | MESSAGE_TIMEOUT_MS, LONG_MESSAGE_TIMEOUT_MS 追加 |
| rea-admin/src/components/form/DynamicForm.tsx | setTimeout(3000) → MESSAGE_TIMEOUT_MS（8箇所） |
| rea-admin/src/components/form/FieldFactory.tsx | setTimeout(3000/5000) → 定数（5箇所） |
| rea-admin/src/components/form/LocationField.tsx | setTimeout(3000) → MESSAGE_TIMEOUT_MS（1箇所） |
| rea-admin/src/components/form/RegulationTab.tsx | setTimeout(3000) → MESSAGE_TIMEOUT_MS（1箇所） |
| rea-admin/src/pages/Settings/IntegrationsPage.tsx | setTimeout(3000/5000) → 定数（2箇所） |
| rea-admin/src/pages/Settings/UsersPage.tsx | setTimeout(3000/5000) → 定数（2箇所） |
| rea-admin/src/pages/Settings/SystemSettingsPage.tsx | setTimeout(3000) → MESSAGE_TIMEOUT_MS（1箇所） |
| rea-admin/src/pages/Properties/PropertyEditDynamicPage.tsx | setTimeout(3000) → MESSAGE_TIMEOUT_MS（1箇所） |
| rea-admin/src/pages/admin/FieldVisibilityPage.tsx | setTimeout(3000) → MESSAGE_TIMEOUT_MS（2箇所） |

---

## 変更概要

ハードコードされたsetTimeoutの遅延値（3000ms/5000ms）を定数ファイルに集約。
ロジックの変更なし。値の変更なし。import追加と定数参照への置換のみ。

---

## テストケース

### 正常系 - メッセージ自動消去（3秒）

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | 学区検索エラー | 緯度経度なしで学区検索ボタン押下 | エラーメッセージが3秒後に消える |
| 2 | 駅検索エラー | 緯度経度なしで駅検索ボタン押下 | エラーメッセージが3秒後に消える |
| 3 | バス停検索エラー | 緯度経度なしでバス停検索ボタン押下 | エラーメッセージが3秒後に消える |
| 4 | 施設検索エラー | 緯度経度なしで施設検索ボタン押下 | エラーメッセージが3秒後に消える |
| 5 | 法令制限取得成功 | 有効座標で法令制限取得 | 成功メッセージが3秒後に消える |
| 6 | ジオコード完了 | 住所入力→座標取得 | ステータスが3秒後にリセット |
| 7 | 連携設定更新 | 外部連携設定を更新 | 成功メッセージが3秒後に消える |
| 8 | ユーザー有効/無効切替 | ユーザー一覧で有効/無効ボタン押下 | 成功メッセージが3秒後に消える |
| 9 | システム設定保存 | システム設定を変更して保存 | 成功メッセージが3秒後に消える |
| 10 | ZOHO同期 | 物件編集画面でZOHO同期実行 | ステータスが3秒後にリセット |
| 11 | フィールド表示設定保存 | フィールド表示設定を変更して保存 | メッセージが3秒後に消える |

### 正常系 - メッセージ自動消去（5秒）

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 12 | 用途地域検索エラー | 住所なしで法令調査ボタン押下 | エラーメッセージが5秒後に消える |
| 13 | 用途地域検索完了 | 有効住所で法令調査ボタン押下 | 結果メッセージが5秒後に消える |
| 14 | ユーザー作成成功 | 新規ユーザー作成 | 成功メッセージが5秒後に消える |
| 15 | 一括同期完了 | 外部連携で一括同期実行 | 結果メッセージが5秒後に消える |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 16 | レグレッション | メッセージの表示/非表示タイミングが変更前と同一であること |
| 17 | TypeScript | ビルドエラーなし（tsc --noEmit通過済み） |

---

## テスト環境

- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
