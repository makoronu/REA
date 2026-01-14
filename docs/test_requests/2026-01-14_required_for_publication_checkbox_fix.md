# テスト依頼書: 公開時必須設定チェックボックス修正

## 作成日
2026-01-14

## 概要
管理画面のフィールド設定で「公開時必須設定」のチェックボックスが正しく動作しない問題を修正

---

## 変更内容

| 対象 | 変更内容 |
|------|---------|
| FieldVisibilityPage.tsx | nullの意味をsettingTypeで分岐するよう修正 |

---

## 技術的変更点

### 根本原因
`visible_for`と`required_for_publication`で`null`の意味が異なる：
- `visible_for = null`: 全種別で表示（チェックON）
- `required_for_publication = null`: 必須ではない（チェックOFF）

### 修正関数（4つ）

| 関数 | 修正内容 |
|------|---------|
| `isChecked` | `null`判定を`settingType`で分岐 |
| `handleToggle` | トグル時の`null`⇔配列変換ロジックを分岐 |
| `handleRowSelectAll` | 行の全選択/全解除を分岐 |
| `handleColSelectAll` | 列の全選択/全解除を分岐 |

---

## テスト項目

### 正常系（公開時必須設定タブ）

| # | テスト内容 | 期待結果 | 確認 |
|---|----------|---------|------|
| 1 | 必須タブで未設定（null）のフィールドを表示 | チェックボックスがOFF | [ ] |
| 2 | チェックをONにして保存 | DBに配列が設定される | [ ] |
| 3 | チェックをOFFにして保存 | DBから種別が除外される | [ ] |
| 4 | 「全」ボタン（列）をクリック | 全種別がONになる | [ ] |
| 5 | 「無」ボタン（列）をクリック | 全種別がOFFになる | [ ] |
| 6 | 「全」ボタン（行）をクリック | その種別が全フィールドでONになる | [ ] |

### 確認用SQL

```sql
-- 変更前後の確認
SELECT column_name, required_for_publication, updated_at, updated_by
FROM column_labels
WHERE table_name = 'properties'
ORDER BY updated_at DESC NULLS LAST
LIMIT 10;
```

### 異常系（リグレッション）

| # | テスト内容 | 期待結果 | 確認 |
|---|----------|---------|------|
| 7 | 表示設定タブでnullのフィールドを表示 | チェックボックスがON | [ ] |
| 8 | 表示設定タブでチェックをOFF→保存 | 正常に動作 | [ ] |
| 9 | 表示設定タブで「全」ボタン | 正常に動作（null設定） | [ ] |

---

## テスト環境

- URL: https://realestateautomation.net/
- 管理画面: /admin/field-visibility

## 備考

- フロントエンド修正のみ、DB変更なし
- API（admin.py）は正常に動作確認済み
