# テスト依頼: metadata API option_code INTEGER変換

**依頼日:** 2026-01-04
**コミット:** (コミット後に記入)

---

## テスト対象

| ファイル | 変更内容 |
|---------|---------|
| `rea-api/app/api/api_v1/endpoints/metadata.py` | option_codeを数値に変換する関数追加・適用 |

---

## 変更概要

- `_convert_option_code_to_int()` 関数を追加
- `'rea_1'` → `1`, `'rea_2'` → `2` のように数値変換
- 対象: `_get_master_options_cache`, `get_options_by_category` 関数

---

## 対象カラム（land_infoテーブル）

- setback（セットバック）
- terrain（地勢）
- city_planning（都市計画）
- land_category（地目）
- land_rights（土地権利）
- land_transaction_notice（国土法届出）
- land_area_measurement（土地面積計測方式）

---

## テスト手順

### 1. API応答確認

```bash
# 各カテゴリのオプションがINTEGERで返されることを確認
curl -s http://localhost:8005/api/v1/metadata/options/city_planning | python3 -m json.tool

# 期待: "value": 1, "value": 2 等（"rea_1", "rea_2"ではない）
```

確認項目:
- [ ] city_planning: value が 1, 2, 3, 4（数値）
- [ ] setback: value が 1, 2（数値）
- [ ] terrain: value が 1, 2, 3, ...（数値）
- [ ] land_category: value が 1, 2, 3, ...（数値）

### 2. 物件編集画面での表示確認

1. 物件編集画面を開く
2. 「土地情報」タブに移動
3. 以下を確認:
   - [ ] セットバック: 「無」「有」のみ表示
   - [ ] 地勢: 「平坦」「高台」等のみ表示
   - [ ] 都市計画: 「市街化区域」等のみ表示
   - [ ] 地目: 「宅地」「田」等のみ表示

### 3. 保存確認

1. 上記フィールドで値を選択
2. 保存ボタンをクリック
3. 以下を確認:
   - [ ] エラーなく保存できる
   - [ ] 画面リロード後も値が保持される

### 4. DB確認

```sql
-- 保存後にDBで確認
SELECT id, setback, terrain, city_planning, land_category
FROM land_info
WHERE property_id = [テストした物件ID];
```

- [ ] 値がINTEGER（1, 2, 3等）で保存されている

---

## 異常系テスト

### 境界値

- [ ] 各フィールドで「未選択」→ 保存 → NULLで保存される
- [ ] 各フィールドで値選択 → 別の値に変更 → 保存 → 正しく更新される

---

## テスト環境

```bash
# API起動
cd ~/my_programing/REA/rea-api
PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005

# フロント起動
cd ~/my_programing/REA/rea-admin
npm run dev
```

URL: http://localhost:5173

---

## 期待結果

- APIが option_code を INTEGER（1, 2, 3...）で返す
- フロントエンドは INTEGER を受け取り、INTEGER を送信する
- DBの INTEGER カラムに正しく保存される
- rea_* 形式のコードは表示されない・送信されない
