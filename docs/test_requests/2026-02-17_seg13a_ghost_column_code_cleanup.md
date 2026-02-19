# テスト依頼書: Seg 13a - ゴーストカラム物理削除（コード修正）

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| properties.py:436-476 | 元請会社APIエンドポイント削除 |
| metadata.py:699,711,742-743 | shows_contractor参照削除 |
| metadata.py:877-893 | contractor_requiredクエリ削除 |
| metadataService.ts:317,342-344 | 型定義削除 |
| publication_validator.py:28,73 | コメント整理 |
| fill_dummy_property.py:25-55 | ダミーデータからゴーストカラム参照削除 |

---

## 変更概要

本番DBから物理削除予定の25カラム（Seg 13b）に先立ち、コード側の参照を削除。元請会社連絡先APIエンドポイント（未使用）削除。メタデータAPIからshows_contractor/contractor_required削除。フロントエンド型定義整理。

---

## テストケース

### 正常系

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | フロントエンド表示 | トップページアクセス | 正常に表示される |
| 2 | API認証 | ログイン → 物件一覧表示 | 正常に動作する |
| 3 | 物件編集 | 既存物件を編集→保存 | 正常に保存される |
| 4 | メタデータAPI | マスタオプション取得 | shows_contractorフィールドが含まれない |
| 5 | ステータス設定API | /api/v1/metadata/status-settings | transaction_typeキーが含まれない |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 6 | 削除エンドポイント | GET /api/v1/properties/contractors/contacts → 404 |
| 7 | レグレッション | 物件CRUD全操作が正常動作すること |
| 8 | 公開バリデーション | 公開前確認バリデーションが正常動作すること |

---

## テスト環境

- API: `cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005`
- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
