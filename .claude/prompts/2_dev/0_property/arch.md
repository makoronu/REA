# アーキテクチャ

## 設計思想
- **メタデータ駆動**: column_labelsがマスター
- **GenericCRUD**: rea-api/app/crud/generic.py

## テーブル構成
```
properties（親）
  ├─ building_info
  ├─ land_info
  ├─ property_images
  └─ property_registries
```

## column_labels重要カラム
| カラム | 意味 |
|--------|------|
| visible_for | NULL=全表示, []=非表示, ['mansion']=指定のみ |
| required_for_publication | 公開時必須種別 |
| master_category_code | マスタ連携キー |

## 物件種別
mansion, apartment, detached, office, store, warehouse, factory, building

## 次 → traps.md
