# テスト依頼書: Seg 8a - console.log削除・zoho naive datetime修正

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| rea-admin/src/components/form/DynamicForm.tsx | console.log('Save button clicked') 削除 |
| rea-admin/src/components/form/ZoningMapField.tsx | console.log('ZoningMap: Initializing at') 削除 |
| rea-api/app/services/zoho/auth.py | datetime.now()→datetime.now(timezone.utc)（3箇所） |
| rea-api/app/services/zoho/mapper.py | zoho_synced_at をdatetime.now(timezone.utc)に修正 |

---

## 変更概要

コード品質修正6件。本番残留していたconsole.logデバッグ文2件を削除。Zoho連携のnaive datetime（タイムゾーン未指定）4件をUTC明示化。

---

## テストケース

### 正常系

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | 物件保存 | 物件編集→保存ボタンクリック | 正常に保存される |
| 2 | 用途地域マップ表示 | 法令調査→用途地域マップ | 地図が正常に表示される |
| 3 | Zoho同期（設定済み環境のみ） | Zohoインポート実行 | トークン取得・データ同期が正常に動作 |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 4 | console.log残留確認 | DevToolsでDynamicForm保存時にconsole.logが出ないこと |
| 5 | console.log残留確認 | DevToolsでZoningMapField初期化時にconsole.logが出ないこと |
| 6 | レグレッション（保存） | 物件保存の通常フローが壊れていないこと |
| 7 | レグレッション（地図） | 用途地域マップの表示・操作が壊れていないこと |
| 8 | TypeScript | ビルドエラーなし（tsc --noEmit通過済み） |
| 9 | Python | コンパイルエラーなし（py_compile通過済み） |

---

## テスト環境

- API: `cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005`
- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
