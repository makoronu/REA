# テストレポート: land_info オプション修正

**テスト日:** 2026-01-04
**コミット:** 148da1c
**テスター:** Claude Code (自動テスト)

---

## サマリー

| 項目 | 結果 |
|------|------|
| オプション表示確認 | ✅ PASS |
| DB型確認 | ✅ PASS |
| 保存テスト | ❌ FAIL |
| 異常系テスト | ❌ FAIL |
| 攻撃ポイント | ⚠️ 要確認 |

---

## 重大な問題

### land_info の保存が機能していない

APIでPUT /properties/{id}に`land_info`を送信しても、DBに保存されない。

```
テスト物件ID: 2480
送信データ: {"land_info": {"setback": 1, "terrain": 2}}
APIレスポンス: 200 OK
DB確認: setback=NULL, terrain=NULL（変更なし）
```

**原因調査が必要。**

---

## 1. オプション表示確認

### API `/api/v1/metadata/options/{category}` 確認結果

| カラム | 結果 | 値形式 |
|--------|------|--------|
| setback | ✅ PASS | `"1"`, `"2"` (INTEGER) |
| terrain | ✅ PASS | `"1"`〜`"9"` (INTEGER) |
| city_planning | ✅ PASS | `"1"`〜`"4"` (INTEGER) |
| land_category | ✅ PASS | `"1"`〜`"11"` (INTEGER) |
| land_rights | ✅ PASS | `"1"`〜`"99"` (INTEGER) |
| land_transaction_notice | ⚠️ カテゴリ未定義 | - |
| land_area_measurement | ⚠️ カテゴリ未定義 | - |

**判定:** `rea_*` 形式のコードなし → **PASS**

---

## 2. DB確認

### カラム型確認

| カラム | 型 | 結果 |
|--------|-----|------|
| setback | INTEGER | ✅ |
| terrain | INTEGER | ✅ |
| city_planning | INTEGER | ✅ |
| land_category | INTEGER | ✅ |
| land_rights | INTEGER | ✅ |
| land_transaction_notice | INTEGER | ✅ |
| land_area_measurement | INTEGER | ✅ |

**判定:** 全7カラムがINTEGER型 → **PASS**

---

## 3. 保存テスト

### Test 1: INTEGER値で保存

```
送信: {"land_info": {"setback": 1, "terrain": 2, "city_planning": 1}}
Status: 200 OK
結果: ❌ FAIL（値が保存されない）
```

### Test 2: 値変更

```
送信: {"land_info": {"setback": 2, "terrain": 1}}
Status: 200 OK
結果: ❌ FAIL（値が更新されない）
```

### Test 3: NULL値で保存

```
送信: {"land_info": {"setback": null}}
Status: 200 OK
結果: ✅ PASS（元からNULL）
```

---

## 4. 攻撃ポイントテスト

### Test 4: 不正値 'rea_1' 送信

```
送信: {"land_info": {"setback": "rea_1"}}
Status: 200 OK
保存された値: NULL
結果: ⚠️ エラーにならず無視された（要確認）
```

### Test 5: 範囲外の値 '999' 送信

```
送信: {"land_info": {"setback": 999}}
Status: 200 OK
保存された値: NULL
結果: ⚠️ エラーにならず無視された（FK制約なし）
```

---

## 5. 発見事項

### 要修正

1. **land_info の保存が機能していない**
   - APIは200を返すが、DBに反映されない
   - 原因調査・修正が必要

2. **バリデーションなし**
   - 不正値（文字列、範囲外）がエラーにならず無視される
   - 外部キー制約またはバリデーション追加を検討

### 要確認

1. **カテゴリ未定義**
   - `land_transaction_notice` (国土法届出)
   - `land_area_measurement` (土地面積計測方式)

---

## 6. DB確認結果

```sql
SELECT id, property_id, setback, terrain, city_planning
FROM land_info
WHERE property_id = 2480;

  id  | property_id | setback | terrain | city_planning
------+-------------+---------+---------+---------------
 2355 |        2480 |         |         |
```

テスト後もNULLのまま。

---

## 結論

### PASS

- オプション値: INTEGER形式（`"1"`, `"2"`, ...）で返却 ✅
- DB型: INTEGER ✅
- `rea_*` 形式: なし ✅

### FAIL

- **land_info の保存が機能していない** ❌
- デプロイ前に修正が必要

---

## 次のアクション

1. land_info保存機能の原因調査
2. 修正後、再テスト実施
