# 既知の罠

## 毎回確認せよ

| 罠 | 正 | 誤 |
|----|----|----|
| 全種別表示 | visible_for = NULL | visible_for = [] |
| ラベル名 | japanese_label | label_ja |
| グループ名 | group_name | field_group |
| property_locations | geom列なし | geom参照 |

## 変更前に確認
```sql
-- column_labelsカラム一覧
SELECT column_name FROM information_schema.columns
WHERE table_name = 'column_labels';

-- 対象テーブルカラム一覧
SELECT column_name FROM information_schema.columns
WHERE table_name = '[対象テーブル]';
```

## 次 → checklist.md
