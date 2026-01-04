# テストレポート: Seg5 ステータス連動

**テスト日:** 2026-01-04
**テスター:** Claude Code (自動テスト)

---

## サマリー

| # | 操作 | 期待結果 | 実際 | 結果 |
|---|------|---------|------|------|
| 1 | 販売中に変更 | 公開前確認 | 公開前確認 | ⚠️ 偽陽性 |
| 2 | 成約済みに変更 | 非公開 | 公開前確認 | ❌ FAIL |
| 3 | 取下げに変更 | 非公開 | 未テスト | - |
| 4 | 販売終了に変更 | 非公開 | 公開前確認 | ❌ FAIL |

**総合判定: ❌ FAIL - 全ての連動が動作していない**

---

## 根本原因（確定）

### 問題: `properties.sales_status` と `master_options.option_code` の型不整合

**DBの実際のデータ:**

| テーブル | カラム | 値 | 型 |
|---------|--------|-----|-----|
| properties | sales_status | `3` | INTEGER |
| master_options | option_code | `rea_3` | VARCHAR |

**マッピング関係:**
```
properties.sales_status = 3
↓
master_options.option_code = 'rea_' + '3' = 'rea_3'
```

### 問題のコード: `get_status_trigger_codes` 関数

**場所:** `rea-api/app/api/api_v1/endpoints/properties.py:33-61`

```python
def get_status_trigger_codes(db: Session, trigger_type: str) -> List[int]:
    query = text(f"""
        SELECT mo.option_code  # ← 'rea_3' を取得
        FROM master_options mo
        ...
    """)
    result = db.execute(query)
    codes = []
    for row in result:
        code = row.option_code  # code = 'rea_3'
        if code and str(code).isdigit():  # ← 'rea_3'.isdigit() = False
            codes.append(int(code))
    return codes  # ← 常に空リスト []
```

### 連動ロジックの失敗

```python
sales_code = int(new_sales_status)  # sales_code = 3
pre_check_codes = get_status_trigger_codes(db, 'triggers_pre_check')  # = []
if sales_code in pre_check_codes:  # 3 in [] = False
    property_data["publication_status"] = "公開前確認"  # 実行されない
```

---

## テスト1が「PASS」に見えた理由

```
テスト前: sales_status=3, publication_status=公開前確認
テスト後: sales_status=3, publication_status=公開前確認（変化なし）
```

**実際は連動が動作していない。元々「公開前確認」だったため、変化がなかっただけ。**

---

## DB確認結果

### master_options（sales_status）

```
 option_code  | option_value | triggers_unpublish | triggers_pre_check
--------------+--------------+--------------------+--------------------
 rea_1        | 準備中       | f                  | f
 rea_2        | 販売準備     | f                  | f
 rea_3        | 販売中       | f                  | t  ← 公開前確認トリガー
 rea_4        | 商談中       | f                  | f
 契約予定     | 契約予定     | f                  | f
 決済予定     | 決済予定     | f                  | f
 契約決済予定 | 契約決済予定 | f                  | f
 rea_5        | 成約済み     | t                  | f  ← 非公開トリガー
 rea_6        | 販売終了     | t                  | f  ← 非公開トリガー
```

### properties（ID: 2480）

```
 sales_status | publication_status
--------------+--------------------
 3            | 公開前確認
```

---

## 修正方針

`get_status_trigger_codes` 関数を以下のように修正する必要がある：

**修正案1:** `option_code` から数値部分を抽出
```python
# 'rea_3' → 3
if code and code.startswith('rea_'):
    codes.append(int(code.replace('rea_', '')))
```

**修正案2:** 専用の数値カラムを追加
```sql
ALTER TABLE master_options ADD COLUMN sales_status_int INTEGER;
UPDATE master_options SET sales_status_int = 3 WHERE option_code = 'rea_3';
-- etc.
```

---

## 結論

**❌ FAIL - 全てのステータス連動が動作していない**

### 根本原因

1. `properties.sales_status` は INTEGER（例: `3`）
2. `master_options.option_code` は VARCHAR（例: `rea_3`）
3. `get_status_trigger_codes` 関数が `option_code.isdigit()` でフィルタ
4. `rea_3` は数字ではないので、フィルタで除外される
5. 結果として常に空リストが返り、全ての連動が失敗

### 必要なアクション

1. 開発者による `get_status_trigger_codes` 関数の修正
2. `option_code` から `rea_` プレフィックスを除去して比較する処理を追加
3. 修正後、再テスト実施
