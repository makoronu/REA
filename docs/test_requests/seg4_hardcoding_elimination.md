# Seg4 ハードコーディング撲滅 テスト依頼書

**作成日**: 2026-01-04
**対象**: 定数ファイル作成・placeholder DB化

---

## 変更概要

| 分類 | 内容 |
|------|------|
| DB変更 | column_labels.placeholder カラム追加 |
| 新規ファイル | errors.py, placeholders.ts, dateFormat.ts, date_format.py |
| 修正ファイル | metadata.py |

---

## テスト項目

### 1. マイグレーション確認（本番デプロイ後）

```sql
-- placeholderカラムが追加されていることを確認
SELECT column_name FROM information_schema.columns
WHERE table_name = 'column_labels' AND column_name = 'placeholder';
```

**期待結果**: 1行返却

---

### 2. メタデータAPI確認

```bash
# column情報にplaceholderが含まれることを確認
curl -s "http://localhost:8005/api/v1/metadata/properties/columns" | jq '.[0].placeholder'
```

**期待結果**: `null`（現時点ではデータ未投入）

---

### 3. フロントエンド動作確認

1. ログインページ表示
   - メールアドレス欄に `mail@example.com` が表示されること
   - パスワード欄に `********` が表示されること

2. 物件編集画面表示
   - 各フィールドにplaceholderが表示されること
   - エラーが発生しないこと

---

### 4. インポート確認

```bash
# Python
cd rea-api && PYTHONPATH=.. python3 -c "from app.core.errors import ErrorMessages; print(ErrorMessages.PROPERTY_NOT_FOUND)"

# TypeScript
cd rea-admin && npx tsc --noEmit
```

**期待結果**:
- Python: `物件が見つかりません`
- TypeScript: エラーなし

---

## 注意事項

- 今回はDB構造変更のみ、実際のplaceholderデータ投入は別タスク
- 既存の動作には影響なし（column.placeholderがnullの場合はフォールバック）

---

## 判定基準

- [ ] マイグレーション成功
- [ ] メタデータAPI正常動作
- [ ] フロントエンド正常表示
- [ ] 型チェック成功
