# メタデータ駆動 診断レポート

**診断日**: 2025-12-15
**診断者**: Claude

---

## 結論

**メタデータ駆動は「表示層」のみ実装されており、「データ層」は完全にハードコード**

| Layer | 状態 | 問題 |
|-------|------|------|
| DB → API | ❌ 破綻 | モデル/スキーマが全てハードコード |
| API → フロント | △ 部分的 | DynamicFormはメタデータ使用、だが型定義がハードコード |
| 全体フロー | ❌ 破綻 | カラム追加時に7ファイル以上の修正が必要 |

---

## 問題の詳細

### 1. バックエンド（致命的）

#### models/property.py（44カラム全てハードコード）
```python
# 現状: ❌ ハードコード
class Property(Base):
    id = Column(Integer, primary_key=True)
    property_name = Column(String(255))
    sale_price = Column(Numeric(15, 2))
    # ... 44カラム全て手書き
```

**問題点**:
- カラム追加時にこのファイルを修正する必要がある
- DBスキーマとコードが二重管理になっている

#### schemas/property.py（全フィールドハードコード）
```python
# 現状: ❌ ハードコード
class PropertyBase(BaseModel):
    company_property_number: Optional[str] = None
    property_name: Optional[str] = None
    # ... 全フィールド手書き
```

**問題点**:
- models/property.pyと同じフィールドを二重定義
- バリデーションルールもハードコード

#### crud/property.py
```python
# 現状: ❌ ハードコード
SORTABLE_COLUMNS = {
    "id": Property.id,
    "property_name": Property.property_name,
    # ...
}
```

#### properties.py（APIエンドポイント）
```python
# 現状: ❌ クエリパラメータがハードコード
property_type: Optional[str] = Query(None)
sales_status: Optional[str] = Query(None)
```

### 2. フロントエンド（部分的に問題）

#### types/property.ts（全フィールドハードコード）
```typescript
// 現状: ❌ ハードコード
export interface Property {
  id: number;
  property_name?: string;
  sale_price?: number;
  // ... 全フィールド手書き
}
```

**問題点**:
- バックエンドと同じフィールドを三重定義（models, schemas, types）
- 型安全性のために必要だが、メタデータ駆動と相反

#### DynamicForm.tsx（部分的にメタデータ駆動）
```typescript
// ✅ メタデータから動的にフィールド生成
columns.map(col => <Field key={col.column_name} ... />)

// ❌ しかし特殊フィールドはハードコード
if (column_name === 'road_info') return <RoadInfoEditor />
if (column_name === 'transportation') return <TransportationField />
```

---

## ハードコード箇所一覧

### バックエンド（7ファイル）

| ファイル | 問題 | 影響度 |
|---------|------|-------|
| `models/property.py` | 44カラム全てハードコード | 致命的 |
| `schemas/property.py` | 全フィールドハードコード | 致命的 |
| `crud/property.py` | SORTABLE_COLUMNS、検索条件 | 高 |
| `properties.py` | クエリパラメータ、/fullの結合ロジック | 高 |
| `touki.py` | 登記データのカラム名 | 中 |
| `zoho.py` | マッピングフィールド | 中 |
| `equipment.py` | 設備フィールド | 低 |

### フロントエンド（12ファイル）

| ファイル | 問題 | 影響度 |
|---------|------|-------|
| `types/property.ts` | Property interface全体 | 致命的 |
| `types/propertyTables.types.ts` | PropertyMain等の型定義 | 高 |
| `PropertiesPage.tsx` | テーブル列定義 | 高 |
| `CommandPalette.tsx` | 検索対象フィールド | 中 |
| `FieldFactory.tsx` | 特殊フィールド判定 | 中 |
| `DynamicForm.tsx` | 特殊フィールド処理 | 中 |
| `LocationField.tsx` | 住所フィールド構成 | 低 |
| `TransportationField.tsx` | 交通フィールド構成 | 低 |
| `PropertyEditPage.tsx` | 旧版（削除可能） | 低 |
| `PropertyEditPageAutoSave.tsx` | 旧版（削除可能） | 低 |
| `PropertyEditPageV2.tsx` | V2版（削除可能） | 低 |
| `PropertyTabs.tsx` | タブ構成 | 低 |

---

## 根本原因

### 1. 最初から実装されていなかった
- SQLAlchemy ORM + Pydantic の典型的なパターンを採用
- このパターン自体がハードコード前提

### 2. メタデータ駆動の範囲が「表示層」に限定
- `column_labels`テーブルは存在する
- DynamicFormはこれを使って動的にフォームを生成
- しかしデータ層（CRUD）は別系統

### 3. 型安全性との二律背反
- TypeScriptの型定義はコンパイル時に必要
- メタデータ駆動（ランタイム）と相反

---

## 修正方針

### Phase 1: 即効性のある修正（今日やる）

#### 1.1 /fullエンドポイントの住所上書き問題を修正
```python
# properties.py:117-119 を修正
for key, value in land_dict.items():
    if key not in ['id', 'property_id', 'created_at', 'updated_at']:
        # NULLの場合は上書きしない
        if value is not None or key not in result:
            result[key] = value
```

### Phase 2: 中期的な改善（1週間）

#### 2.1 動的スキーマの導入
```python
# 新しいアプローチ: column_labelsからPydanticモデルを動的生成
def create_dynamic_schema(table_name: str):
    columns = db.query(ColumnLabel).filter_by(table_name=table_name).all()
    fields = {}
    for col in columns:
        fields[col.column_name] = (Optional[str], None)
    return create_model(f'{table_name}Schema', **fields)
```

#### 2.2 汎用CRUDの作成
```python
# generic_crud.py
class GenericCRUD:
    def get(self, table_name: str, id: int):
        return db.execute(text(f"SELECT * FROM {table_name} WHERE id = :id"), {"id": id})

    def update(self, table_name: str, id: int, data: dict):
        # column_labelsから有効なカラムのみ許可
        valid_columns = get_valid_columns(table_name)
        filtered_data = {k: v for k, v in data.items() if k in valid_columns}
        # ...
```

### Phase 3: 長期的な改善（1ヶ月）

#### 3.1 フロントエンドの型定義を動的化
- OpenAPI schemaから型を自動生成
- または `any` 型を許容してランタイムバリデーション

#### 3.2 旧ファイルの削除
- PropertyEditPage.tsx（旧版）
- PropertyEditPageAutoSave.tsx（旧版）
- PropertyEditPageV2.tsx（V2版）
- types/propertyTables.types.ts（未使用）

---

## 共通化すべきコード

### 1. カラム名のリスト
現状:
- models/property.py
- schemas/property.py
- types/property.ts
→ 3箇所で同じリストを管理

対策: column_labelsテーブルを唯一の真実とする

### 2. ENUM値
現状:
- column_labels.enum_values
- master_options
- property_types
→ 3系統が混在

対策: master_optionsに統一

### 3. 特殊フィールドの処理
現状:
- DynamicForm.tsx
- FieldFactory.tsx
- JsonEditors.tsx
→ 複数箇所で同じ判定ロジック

対策: column_labelsにinput_typeを追加して統一管理

---

## 次のアクション

1. **今すぐ**: 住所上書き問題を修正（properties.py:117-119）
2. **今日中**: 旧版ファイルの削除（3ファイル）
3. **今週中**: 動的スキーマの検討・プロトタイプ作成
4. **来週**: 汎用CRUDの実装

---

## 参考: 理想的なメタデータ駆動アーキテクチャ

```
┌─────────────────┐
│  column_labels  │  ← 唯一の真実
│   (143カラム)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │ 自動生成 │
    └────┬────┘
         │
┌────────┼────────┐
│        │        │
▼        ▼        ▼
Model   Schema   Type
(Python) (Pydantic) (TypeScript)
```

現状は3箇所を手動で同期しているため、不整合が発生する。
