# テストレポート: metadata API option_code INTEGER変換

**テスト日:** 2026-01-04
**コミット:** 5c9bd31
**テスター:** Claude Code (自動テスト)

---

## サマリー

| 項目 | 結果 |
|------|------|
| API応答（INTEGER変換） | ✅ PASS |
| 保存テスト | ❌ FAIL |
| DB確認 | ❌ FAIL |

---

## 1. API応答確認（INTEGER変換）

### 結果: ✅ PASS

```
■ city_planning:
  value=1 (int): 市街化区域
  value=2 (int): 市街化調整区域
  value=3 (int): 非線引区域
  value=4 (int): 都市計画区域外

■ setback:
  value=1 (int): 無
  value=2 (int): 有

■ terrain:
  value=1 (int): 平坦
  value=2 (int): 高台
  value=3 (int): 低地
  value=4 (int): ひな段
  value=5 (int): 傾斜地
```

- `value`がint型で返される ✅
- `rea_*`形式なし ✅

---

## 2. 保存テスト

### 結果: ❌ FAIL

```
テスト物件ID: 2480

■ Test 1: INTEGER値で保存
  送信: {"land_info": {"setback": 1, "terrain": 2, "city_planning": 1}}
  Status: 200 OK
  レスポンス: setback=None, terrain=None, city_planning=None
  結果: ❌ FAIL（値が保存されない）

■ Test 2: 値変更
  送信: {"land_info": {"setback": 2, "terrain": 1}}
  Status: 200 OK
  レスポンス: setback=None, terrain=None
  結果: ❌ FAIL（値が更新されない）

■ Test 3: NULL値で保存
  結果: ✅ PASS（元からNULL）
```

---

## 3. DB確認

### 結果: ❌ FAIL

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

## 問題分析

### 今回の修正

- `metadata.py`のoption_code変換 → ✅ 成功

### 未修正の問題

- **物件更新API（`PUT /properties/{id}`）がland_infoを保存していない**
- APIは200を返すが、DBに反映されない
- 別の問題（修正対象外）

---

## 結論

### 今回のテスト対象（INTEGER変換）

- **PASS**: APIがINTEGERでオプション値を返す

### 別問題（未修正）

- **FAIL**: land_infoの保存処理が機能していない
- 原因: 物件更新APIのland_info処理に問題あり

---

## 次のアクション

1. ~~metadata API INTEGER変換~~ → ✅ 完了
2. **物件更新APIのland_info保存処理を調査・修正**
