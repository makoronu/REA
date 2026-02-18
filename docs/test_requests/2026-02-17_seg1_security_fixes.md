# テスト依頼書: Seg 1 - セキュリティ修正

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| rea-api/app/main.py | スタックトレースをレスポンスから除去 |
| rea-api/app/api/api_v1/endpoints/settings.py | 認証チェック追加（全エンドポイント） |
| rea-api/app/api/api_v1/endpoints/reinfolib.py | radiusパラメータに上限制約追加（le=5） |
| rea-admin/src/pages/Import/ToukiImportPage.tsx | fetch()→apiサービス置換（認証ヘッダー付与） |
| rea-admin/src/pages/Settings/IntegrationsPage.tsx | fetch()→apiサービス置換（認証ヘッダー付与） |
| rea-admin/src/pages/Settings/SystemSettingsPage.tsx | fetch()→apiサービス置換（認証ヘッダー付与） |

---

## 変更概要

セキュリティ脆弱性5件の修正。スタックトレース公開の防止、認証なしエンドポイントへの認証追加、パラメータ上限の追加、未認証fetch通信のaxios(api)サービスへの置換。

---

## テストケース

### 正常系

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | システム設定表示 | 設定→システム設定ページを開く | 設定一覧が表示される |
| 2 | システム設定更新 | APIキーの「値を変更」→新しい値を入力→保存 | 「設定を保存しました」表示 |
| 3 | 外部連携一覧 | 設定→外部連携管理ページを開く | 連携先カード・同期状態が表示される |
| 4 | 連携ON/OFF | 連携先のトグルスイッチ操作 | 有効/無効が切り替わる |
| 5 | 一括同期 | 物件を選択→一括同期ボタン | 同期完了メッセージ表示 |
| 6 | 登記取込PDF | 登記取込→PDFドラッグ&ドロップ | アップロード成功 |
| 7 | 登記解析 | 未解析PDF→「解析」ボタン | 解析完了メッセージ表示 |
| 8 | 登記→物件登録 | レコード選択→「新規物件登録」 | 物件が作成され編集ページが開く |
| 9 | 登記→既存物件反映 | レコード選択→「既存物件へ反映」→物件ID入力 | 反映成功メッセージ表示 |
| 10 | 法令調査MAP | 物件編集→法令制限タブ→MAP表示→タイルデータ取得 | 正常にGeoJSON表示 |

### 異常系・セキュリティ

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 11 | 未認証でシステム設定API | ログアウト状態でブラウザから`/api/v1/settings/`にアクセス | 401エラー |
| 12 | 未認証で設定更新API | curlで認証なしPUT `/api/v1/settings/GOOGLE_MAPS_API_KEY` | 401エラー |
| 13 | 500エラー時のレスポンス | APIで意図的にエラーを発生させる | tracebackフィールドがレスポンスに含まれない |
| 14 | radius上限超え | `/api/v1/reinfolib/tile/xxx?lat=43&lng=141&radius=100` | 422バリデーションエラー |
| 15 | radius=5（上限値） | `/api/v1/reinfolib/tile/xxx?lat=43&lng=141&radius=5` | 正常にGeoJSON返却 |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 16 | レグレッション | ログイン状態で全機能が変更前と同一に動作すること |
| 17 | 認証境界 | ログイン直後・トークン期限切れ直前で正常動作 |
| 18 | TypeScript | ビルドエラーなし（tsc --noEmit通過済み） |
| 19 | Python | コンパイルエラーなし（py_compile通過済み） |

---

## テスト環境

- API: `cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005`
- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
