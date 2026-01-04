# テスト依頼: land_info input_type修正 + 既存データマイグレーション

**依頼日:** 2026-01-04

---

## テスト対象

| 変更 | 内容 |
|------|------|
| column_labels | city_planning, land_category を radio に変更 |
| land_info.use_district | 2370件を `["rea_*"]` → `[数値]` に変換 |

---

## テスト手順

### 1. API応答確認

```bash
curl -s http://localhost:8005/api/v1/metadata/columns/land_info | python3 -c "
import sys, json
d = json.load(sys.stdin)
for c in d:
    if c['column_name'] in ['city_planning', 'land_category', 'use_district']:
        print(f\"{c['column_name']}: input_type={c.get('input_type')}\")
"
```

期待結果:
- [ ] city_planning: input_type=radio
- [ ] land_category: input_type=radio
- [ ] use_district: input_type=multi_select

### 2. 物件編集画面での表示確認

1. 物件編集画面を開く
2. 「土地情報」または「法令制限」タブに移動
3. 以下を確認:
   - [ ] 都市計画: ラジオボタン（単一選択）
   - [ ] 地目: ラジオボタン（単一選択）
   - [ ] 用途地域: チェックボックス（複数選択可）

### 3. 保存確認

1. 各フィールドで値を選択
2. 保存ボタンをクリック
3. 以下を確認:
   - [ ] エラーなく保存できる
   - [ ] 画面リロード後も値が保持される

### 4. DB確認

```sql
-- use_district が数値形式になっているか確認
SELECT use_district FROM land_info WHERE use_district IS NOT NULL LIMIT 5;
-- 期待: [5], [99], [1] など（["rea_*"]形式ではない）

-- rea_形式が残っていないか確認
SELECT COUNT(*) FROM land_info WHERE use_district::text LIKE '%rea_%';
-- 期待: 0
```

---

## 期待結果

- city_planning, land_category は単一選択（ラジオボタン）
- use_district は複数選択（チェックボックス）
- 既存データの rea_* 形式は全て数値に変換済み
