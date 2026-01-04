# テスト依頼: land_info オプション修正

**依頼日:** 2026-01-04
**コミット:** 148da1c

---

## テスト対象

| ファイル | 変更内容 |
|---------|---------|
| `rea-api/app/api/api_v1/endpoints/metadata.py` | source='homes'に変更（2箇所） |
| `land_info`テーブル | 7カラムをINTEGERに復元 |

---

## 対象カラム

- setback（セットバック）
- terrain（地勢）
- city_planning（都市計画）
- land_category（地目）
- land_rights（土地権利）
- land_transaction_notice（国土法届出）
- land_area_measurement（土地面積計測方式）

---

## テスト手順

### 1. オプション表示確認

1. 物件編集画面を開く
2. 「土地情報」または「法令上の制限」タブに移動
3. 以下を確認:
   - [ ] セットバック: 「無」「有」のみ表示（rea_無、rea_有がないこと）
   - [ ] 地勢: 「平坦」「高台」等のみ表示
   - [ ] 都市計画: 「市街化区域」等のみ表示
   - [ ] 地目: 「宅地」「田」等のみ表示

### 2. 保存確認

1. 上記フィールドで値を選択
2. 保存ボタンをクリック
3. 以下を確認:
   - [ ] エラーなく保存できる
   - [ ] 画面リロード後も値が保持される

### 3. DB確認

```sql
-- 保存後にDBで確認
SELECT id, setback, terrain, city_planning, land_category
FROM land_info
WHERE property_id = [テストした物件ID];
```

- [ ] 値がINTEGER（1, 2, 3等）で保存されている
- [ ] 'rea_1'等の文字列ではない

---

## 異常系テスト

### 境界値

- [ ] 各フィールドで「未選択」→保存→NULLで保存される
- [ ] 各フィールドで値選択→別の値に変更→保存→正しく更新される

---

## 攻撃ポイント

- [ ] 開発者ツールでvalue="rea_1"に書き換え→送信→エラーまたは無視される
- [ ] APIに直接 `{"setback": "rea_1"}` を送信→エラーまたは無視される

---

## テスト環境

```bash
# 事前準備（初回のみ）
psql -h localhost -p 5432 -d real_estate_db -f scripts/migrations/seg4_placeholder_column.sql
psql -h localhost -p 5432 -d real_estate_db -f scripts/migrations/fix_land_info_integer_types.sql

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

- オプションがINTEGERコード（1, 2, 3...）で表示・保存される
- rea_*形式のコードが表示されない・保存されない
