# テスト依頼書: Seg5 ステータス連動ロジックAPI一元化

**作成日**: 2026-01-04
**コミット**: e2ef9ad, 6b14cf0（バグ修正）
**担当**: Claude

---

## 概要

販売ステータス（sales_status）→ 公開ステータス（publication_status）の連動ロジックをAPI側に一元化。フロントエンドはAPIレスポンスでUIを更新する。

---

## 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| `rea-admin/src/pages/Properties/PropertiesPage.tsx` | publication_status自動設定削除、APIレスポンスでUI更新 |
| `rea-admin/src/components/form/DynamicForm.tsx` | publication_status自動設定削除 |
| `rea-admin/src/pages/Properties/PropertyEditDynamicPage.tsx` | APIレスポンスでproperty状態更新 |
| `rea-api/app/api/api_v1/endpoints/properties.py` | 非公開連動ロジック追加（DB駆動） |
| `scripts/migrations/seg5_triggers_unpublish.sql` | master_optionsにtriggers_unpublishカラム追加 |
| `docs/roadmap_hardcoding_elimination.md` | Seg5追加 |

---

## テスト環境

- ローカル: http://localhost:5173
- API: http://localhost:8005
- 本番: https://realestateautomation.net/ （デプロイ後）

---

## テストケース

### 1. 物件一覧ページ（/properties）

| # | 操作 | 期待結果 |
|---|------|---------|
| 1-1 | 販売ステータスを「販売中」に変更 | 公開ステータスが「公開前確認」に自動設定される（APIが処理） |
| 1-2 | 販売ステータスを「成約済み」に変更 | 公開ステータスが「非公開」に自動設定される（APIが処理） |
| 1-3 | 販売ステータスを「取下げ」に変更 | 公開ステータスが「非公開」に自動設定される（APIが処理） |
| 1-4 | 販売ステータスを「販売終了」に変更 | 公開ステータスが「非公開」に自動設定される（APIが処理） |
| 1-5 | 一括選択でステータス変更 | 全物件がAPIレスポンスに従って更新される |

### 2. 物件編集ページ（/properties/{id}/edit）

| # | 操作 | 期待結果 |
|---|------|---------|
| 2-1 | DynamicFormで販売ステータスを「販売中」に変更 | publication_statusは変更されない（保存までは） |
| 2-2 | 保存ボタンをクリック | APIレスポンスでpublication_statusが「公開前確認」に更新される |
| 2-3 | 販売ステータスを「成約済み」に変更して保存 | APIレスポンスでpublication_statusが「非公開」に更新される |
| 2-4 | 販売ステータスを「取下げ」に変更して保存 | APIレスポンスでpublication_statusが「非公開」に更新される |

### 3. 新規物件登録（/properties/new/edit）

| # | 操作 | 期待結果 |
|---|------|---------|
| 3-1 | 販売ステータスを選択 | publication_statusは自動設定されない（デフォルト値のまま） |
| 3-2 | 新規作成後、編集画面にリダイレクト | 正常に動作すること |

---

## 確認コマンド

```bash
# API動作確認（販売中に更新 → 公開前確認が返る）
curl -X PATCH "http://localhost:8005/api/v1/properties/1" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{"sales_status": "販売中"}'

# レスポンス例
{
  "id": 1,
  "sales_status": "販売中",
  "publication_status": "公開前確認",
  ...
}
```

---

## 期待されるAPI動作（properties.py）

| 販売ステータス | 公開ステータス連動 |
|----------------|-------------------|
| 販売中 | → 公開前確認 |
| 成約済み | → 非公開 |
| 取下げ | → 非公開 |
| 販売終了 | → 非公開 |

---

## 合格基準

- [ ] 物件一覧でステータス変更が正しく反映される
- [ ] 物件編集で保存後にAPIレスポンスが反映される
- [ ] TypeScriptビルドエラーなし

---

## 注意点

- フロントエンドはpublication_statusを自動設定しなくなった
- すべての連動ロジックはAPI（properties.py）が処理
- UIはAPIレスポンスを信頼して表示を更新

## テスト前提条件

**DBマイグレーション必須:**
```bash
# ローカルテスト前に実行
psql -d and_and < scripts/migrations/seg5_triggers_unpublish.sql
```

マイグレーション未実施の場合、フォールバック値で動作（成約済み、取下げ、販売終了）
