# テスト依頼書: Seg3b-2 旧月額費用カラムバリデーション整理

**作成日**: 2026-01-16
**対象機能**: 公開時バリデーション

---

## 1. 変更概要

旧月額費用カラム（management_fee, repair_reserve_fund, repair_reserve_fund_base）のバリデーション設定を整理。
非表示カラムだが`required_for_publication`が残っていた不整合を解消。

| 変更箇所 | 変更前 | 変更後 |
|----------|--------|--------|
| column_labels.required_for_publication | `{mansion,apartment}` | NULL |
| column_labels.zero_is_valid | true | false |
| publication_validator.py | 旧カラム参照 | 空set |

---

## 2. テスト対象ファイル

| ファイル | 変更内容 |
|---------|---------|
| `rea-api/app/services/publication_validator.py` | フォールバック定数を空に |
| `column_labels` (DB) | 3レコード更新 |

---

## 3. テストケース

### 3.1 公開バリデーション動作確認

| No | 操作 | 期待結果 |
|----|------|----------|
| 1 | マンション物件を「公開」に変更 | 旧カラム（管理費等）がエラーに出ない |
| 2 | マンション物件を「会員公開」に変更 | 同上 |
| 3 | 必須項目を空にして「公開」に変更 | 他の必須項目のみエラー表示 |

### 3.2 DB確認

```sql
-- 旧カラムの設定確認
SELECT column_name, required_for_publication, zero_is_valid
FROM column_labels
WHERE column_name IN ('management_fee', 'repair_reserve_fund', 'repair_reserve_fund_base');
-- 期待: 全てNULL, false

-- monthly_costsの設定確認
SELECT column_name, visible_for, required_for_publication
FROM column_labels
WHERE column_name = 'monthly_costs';
-- 期待: visible_for = {mansion,apartment}, required_for_publication = NULL
```

---

## 4. 確認手順

1. 管理画面にログイン
2. マンション物件を開く
3. 公開ステータスを「公開」に変更
4. 保存（またはバリデーション実行）
5. 「管理費」「修繕積立金」がエラーに表示されないことを確認

---

## 5. 環境情報

- API: FastAPI（ポート8005）
- DB: PostgreSQL（real_estate_db）
- バックアップ: `/tmp/backup_seg3b2_20260116_191755.sql`

---

## 6. 注意事項

- **動作変更なし**: 旧カラムは既に非表示（visible_for='{}'）のため、
  バリデーション対象外だった（get_required_fieldsがvisible_forをチェック）
- **データ整合性のための整理**: 設定の不整合を解消しただけ
- 既存の公開バリデーション動作に影響なし

---

## 7. ロールバック手順

```bash
# バックアップからリストア
ssh rea-conoha "sudo -u postgres psql real_estate_db < /tmp/backup_seg3b2_20260116_191755.sql"

# APIファイルは git revert で対応
```
