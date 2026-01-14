# テスト依頼書: 管理画面API監査カラム対応

## 作成日
2026-01-14

## 概要
フィールド設定API（visible_for/required_for_publication）でupdated_at, updated_byを設定するよう修正

---

## 変更内容

| 対象 | 変更内容 |
|------|---------|
| admin.py | UPDATE文にupdated_at, updated_byを追加 |

---

## 技術的変更点

- `_execute_field_settings_update`関数に`updated_by`パラメータ追加
- UPDATE文に`updated_at = NOW()`, `updated_by = :updated_by`追加
- エンドポイントで`get_current_user(request)`からユーザー情報取得

---

## テスト項目

### 正常系

| # | テスト内容 | 期待結果 | 確認 |
|---|----------|---------|------|
| 1 | 管理画面でフィールド表示設定を変更 | 保存成功 | [ ] |
| 2 | DBでupdated_atを確認 | 更新日時が設定されている | [ ] |
| 3 | DBでupdated_byを確認 | ログインユーザーのemailが設定されている | [ ] |
| 4 | 管理画面で公開時必須設定を変更 | 保存成功、updated_at/updated_by設定 | [ ] |

### 確認用SQL

```sql
SELECT column_name, updated_at, updated_by
FROM column_labels
WHERE table_name = 'land_info'
ORDER BY updated_at DESC
LIMIT 5;
```

### 異常系（リグレッション）

| # | テスト内容 | 期待結果 | 確認 |
|---|----------|---------|------|
| 5 | 未ログイン状態でAPI呼び出し | エラーまたはupdated_by=NULL | [ ] |
| 6 | 物件編集画面の動作 | 正常に動作 | [ ] |

---

## テスト環境

- URL: https://realestateautomation.net/

## 備考

- プロトコル遵守対応（監査カラム必須）
- 今後column_labelsの運用データ変更は管理画面のみで行うこと
