# admin/ - 管理者専用ページ

## 概要
管理者権限（role_level >= 80）が必要なページを格納。

## ページ一覧

| ファイル | パス | 機能 |
|---------|------|------|
| FieldVisibilityPage.tsx | /admin/field-visibility | フィールド表示設定（物件種別ごと） |

## FieldVisibilityPage.tsx

### 機能
- 物件種別（一戸建て、マンション等）ごとに、どのフィールドを表示するかを設定
- column_labelsテーブルのvisible_forカラムを更新

### 依存API
- `GET /api/v1/admin/property-types` - 物件種別一覧
- `GET /api/v1/admin/field-visibility?table_name=xxx` - フィールド表示設定取得
- `PUT /api/v1/admin/field-visibility/bulk` - 一括更新

### データフロー
```
column_labels.visible_for (text[])
  ↓
フロント: チェックボックスON/OFF
  ↓
API: PUT /bulk で更新
  ↓
物件編集画面: visible_forに基づきフィールド表示/非表示
```

### 課題（2025-12-18）
- [x] GROUP_ORDER ハードコード → APIのgroup_orderを使用（修正済み）
- [ ] TABLE_LABELS ハードコード → APIから取得すべき
- [ ] TYPE_GROUP_ORDER ハードコード → DBから取得すべき

### 修正履歴
- 2025-12-18: GROUP_ORDER削除、APIのgroup_orderでソートするように変更

---
*作成: 2025-12-18*
