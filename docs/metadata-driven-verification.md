# メタデータ駆動 実装検証タスク

## 問題の本質

「DBにデータがあるのに編集画面で表示されない」というバグは、**メタデータ駆動が正しく実装されていれば起きない**。

このバグが起きている = メタデータ駆動が**どこかで破綻している**。

---

## 調査目的

**メタデータ駆動のどの部分が「自動」ではなく「手動」になっているかを特定する**

---

## メタデータ駆動の3層チェック

### Layer 1: DB → API（自動化されているか？）

**確認：** APIがcolumn_labelsから動的にカラムを取得しているか

```bash
# generic APIの実装を確認
cat /workspaces/REA/rea-api/app/api/generic.py
```

**期待する実装：**
```python
# ✅ 正しいメタデータ駆動
def get_record(table_name: str, id: str):
    columns = db.query("SELECT column_name FROM column_labels WHERE table_name = %s", [table_name])
    return db.query(f"SELECT {','.join(columns)} FROM {table_name} WHERE id = %s", [id])
```

**NGパターン：**
```python
# ❌ ハードコード（メタデータ駆動ではない）
def get_property(id: str):
    return db.query("SELECT name, address, price FROM properties WHERE id = %s", [id])
```

**質問：** generic.py以外に個別テーブル用APIが存在するか？存在するならそれが問題。

---

### Layer 2: API → フロント（自動化されているか？）

**確認：** DynamicFormがAPIレスポンスをそのまま使っているか

```bash
# DynamicFormの実装を確認
cat /workspaces/REA/rea-admin/src/components/form/DynamicForm.tsx
```

**期待する実装：**
```tsx
// ✅ 正しいメタデータ駆動
const DynamicForm = ({ data, columns }) => {
  return columns.map(col => (
    <Field key={col.column_name} label={col.label_ja} value={data[col.column_name]} />
  ));
};
```

**NGパターン：**
```tsx
// ❌ ハードコード
const PropertyForm = ({ data }) => {
  return (
    <>
      <Field label="物件名" value={data.name} />
      <Field label="住所" value={data.address} />
    </>
  );
};
```

**質問：** DynamicForm以外に個別フォームコンポーネントが存在するか？

---

### Layer 3: データフロー全体（一気通貫しているか？）

**確認：** 編集画面のデータ取得フローを追跡

```bash
# 編集ページの実装を確認
cat /workspaces/REA/rea-admin/src/pages/PropertyEdit.tsx
# または該当するページコンポーネント
```

**期待するフロー：**
```
1. ページロード
2. GET /api/generic/{table}/{id} を呼ぶ
3. GET /api/metadata/{table} を呼ぶ（column_labels取得）
4. DynamicFormに両方渡す
5. 自動でフォーム生成される
```

**NGフロー：**
```
1. ページロード
2. GET /api/properties/{id} を呼ぶ（個別API）
3. ハードコードされたフォームに渡す
4. column_labelsは参照されない
```

---

## 診断コマンド

### 1. 個別APIの存在確認（あったらNG）
```bash
ls -la /workspaces/REA/rea-api/app/api/
# generic.py 以外に properties.py, land_info.py 等があるか？
```

### 2. 個別フォームの存在確認（あったらNG）
```bash
ls -la /workspaces/REA/rea-admin/src/components/
ls -la /workspaces/REA/rea-admin/src/pages/
# PropertyForm.tsx, LandInfoForm.tsx 等があるか？
```

### 3. ハードコードされたカラム名の検索
```bash
# バックエンド
cd /workspaces/REA/rea-api && grep -rn "SELECT.*FROM properties" app/ --include="*.py"
cd /workspaces/REA/rea-api && grep -rn "SELECT.*FROM land_info" app/ --include="*.py"

# フロントエンド
cd /workspaces/REA/rea-admin/src && grep -rn "\.name\|\.address\|\.price" --include="*.tsx" | grep -v "column"
```

---

## 出力フォーマット

```markdown
## 診断結果

### メタデータ駆動の実装状況

| Layer | 状態 | 問題点 |
|-------|------|--------|
| DB → API | ✅ / ❌ | （具体的な問題） |
| API → フロント | ✅ / ❌ | （具体的な問題） |
| 全体フロー | ✅ / ❌ | （具体的な問題） |

### 破綻している箇所

1. **ファイル:** `/path/to/file.py` L行番号
   **問題:** ハードコードされたSELECT文
   **修正:** column_labelsから動的取得に変更

### 結論

メタデータ駆動が機能していない根本原因：
- [ ] 最初から実装されていなかった
- [ ] 途中で個別実装が追加された
- [ ] 一部のテーブルだけ対応していなかった

### 修正方針

（完全なメタデータ駆動にするために必要な変更）
```

---

## ゴール

「column_labelsにカラム追加 → コード変更ゼロ → 画面に反映」

この状態を達成するために、どこを直すべきか明確にする。
