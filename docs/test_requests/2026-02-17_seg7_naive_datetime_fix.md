# テスト依頼書: Seg 7 - naive datetime統一

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| rea-api/app/api/api_v1/endpoints/portal.py | CSVファイル名タイムスタンプをUTC化 |
| rea-api/app/api/api_v1/endpoints/touki.py | parsed_at・アップロードファイル名タイムスタンプをUTC化 |
| rea-api/app/services/portal/homes_exporter.py | HOMES CSV日時フォールバックをJST明示化（3箇所） |

---

## 変更概要

naive datetime（タイムゾーンなし）を全箇所で明示化。内部用途（ファイル名・メタデータ）はUTC、外部連携（HOMES CSV出力）はJST（Asia/Tokyo）に統一。プロトコル§13「タイムゾーン未指定のdatetime」違反を解消。

---

## テストケース

### 正常系

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | HOMES CSVエクスポート | ポータル管理→物件選択→CSVエクスポート | CSV正常ダウンロード、ファイル名にタイムスタンプ含む |
| 2 | CSV内の日時フォーマット | エクスポートしたCSVを確認 | 日時がyyyy/mm/dd hh:mm:ss形式（JST）で出力 |
| 3 | CSV内のデフォルト日付 | 値がNULLのフィールド | 14日後の日付がyyyy/mm/dd形式で出力 |
| 4 | 登記PDFアップロード | 登記管理→PDFアップロード | ファイル保存成功、ファイル名にタイムスタンプ含む |
| 5 | 登記テキストパース | アップロード→パース実行 | パース結果のparsed_atにISO 8601形式タイムスタンプ（UTC） |

### 異常系・境界値

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 6 | 日付NULLの物件エクスポート | 日付フィールドが空の物件をCSVエクスポート | フォールバックで14日後の日本時間が出力される |
| 7 | 日時NULLの物件エクスポート | 日時フィールドが空の物件をCSVエクスポート | フォールバックで現在の日本時間が出力される |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 8 | レグレッション（HOMES CSV） | CSV全体の出力が壊れていないこと |
| 9 | レグレッション（登記インポート） | PDF→パース→物件作成の一連フローが壊れていないこと |
| 10 | タイムゾーン正確性 | HOMES CSVの日時がJST（UTC+9）であること |
| 11 | Python | コンパイルエラーなし（py_compile通過済み） |

---

## テスト環境

- API: `cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005`
- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
