# 検証レポート: land_info 型変更ミス

**検証日:** 2026-01-04
**プロトコル:** .claude/prompts/1_audit/_main.md

---

## 1. 調査

- land_info 8カラム型不一致（本番INTEGER、ローカルVARCHAR/JSONB）
- 他テーブル正常

## 2. 分析

```
Q1. なぜ型変更？ → rea_1がINTEGERに入らない
Q2. なぜrea_1が来る？ → APIがsource='rea'のoption_codeを返す
Q3. なぜsource='rea'？ → metadata.py:630の設定
Q4. 根本原因 → APIフィルタ設定ミス（source='rea'→'homes'が正）
```

## 3. 判定

**パッチ修正可能**

## 修正内容

1. `metadata.py:630` - source='homes'に変更
2. 7カラムをINTEGERに復元
3. 本番DBからデータ復旧

## 教訓

- APIが返すoption_codeがDB型と整合しているか確認
- source='homes'はINTEGERコード、source='rea'は文字列コード

## 影響範囲

ローカルDBのみ（本番無事）

| カラム | 消失件数 |
|--------|----------|
| land_transaction_notice | 2370 |
| land_area_measurement | 2369 |
| city_planning | 409 |
| terrain | 132 |
| land_rights | 113 |
| land_category | 83 |
| setback | 32 |

## 関連ADR

ADR-0001（マッピング除外を追記）
