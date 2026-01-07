# テスト依頼: Seg3b-1 月額費用JSON化（DB準備）

**作成日**: 2026-01-07
**依頼者**: Claude
**状態**: 本番DB適用済み

---

## 概要

月額費用フィールドをJSONB形式に変更。既存データ（management_fee, repair_reserve_fund, repair_reserve_fund_base）をmonthly_costsカラムにマイグレーション。

---

## テスト対象

### 変更箇所

| 種別 | 対象 | 内容 |
|------|------|------|
| DB | properties.monthly_costs | 新カラム追加（JSONB） |
| DB | 2,277レコード | 既存データマイグレーション |
| DB | column_labels | 新フィールド追加、旧フィールド非表示化 |

### データ構造

```json
{
  "管理費": 10000,
  "修繕積立金": 5000,
  "修繕積立基金": 100000
}
```

---

## テストケース

### 正常系

| # | テスト項目 | 手順 | 期待結果 |
|---|-----------|------|----------|
| 1 | 新カラム存在確認 | DBでmonthly_costsカラム確認 | JSOBNカラムが存在する |
| 2 | データマイグレーション確認 | monthly_costsの件数確認 | 2,277件 |
| 3 | データ整合性確認 | 旧カラムと新カラムの値比較 | 全件一致 |
| 4 | column_labels新フィールド | monthly_costsのレコード確認 | input_type='key_value' |
| 5 | 旧フィールド非表示化 | management_fee等のvisible_for確認 | '{}' |

### 確認コマンド

```sql
-- データ件数
SELECT COUNT(*) FROM properties WHERE monthly_costs IS NOT NULL AND monthly_costs != '{}';
-- 期待: 2277

-- データ整合性
SELECT COUNT(*) FROM properties
WHERE (monthly_costs->>'管理費')::int = management_fee;
-- 期待: 2277

-- column_labels状態
SELECT column_name, input_type, visible_for FROM column_labels
WHERE column_name IN ('monthly_costs', 'management_fee');
```

---

## 注意事項

- **フロント非対応**: input_type='key_value'はSeg3b-3で実装予定
- **旧カラム保持**: 検証完了までmanagement_fee等は削除しない

---

## バックアップ

```
/tmp/backup_seg3b1_20260107_130817.sql (944MB)
```

---

## ロールバック手順

```bash
# バックアップからリストア
ssh rea-conoha "sudo -u postgres psql real_estate_db < /tmp/backup_seg3b1_20260107_130817.sql"
```

---

## 次のセグメント

- Seg3b-2: API修正（バリデーション対応）
- Seg3b-3: フロント対応（JSON入力UI）
- Seg3b-4: 旧カラム削除・クリーンアップ
