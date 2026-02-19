# テスト依頼書: Seg 11 - deleted_at漏れ+naive datetime+SQLi防御

**日付:** 2026-02-17
**対象コミット:** (未コミット)

---

## テスト対象

| ファイル | 変更内容 |
|----------|----------|
| touki.py:967 | UPDATE文にAND deleted_at IS NULL追加 |
| real_estate_utils.py:7,166,392 | datetime.now()→datetime.now(timezone.utc) |
| properties.py:51-55 | trigger_typeホワイトリスト検証追加 |

---

## 変更概要

touki.pyの登記インポート論理削除でdeleted_atフィルタ漏れを修正。real_estate_utils.pyの築年数計算でnaive datetimeをtimezone-aware化。properties.pyのステータス連動クエリでtrigger_typeパラメータにホワイトリスト検証を追加。

---

## テストケース

### 正常系

| # | テスト | 手順 | 期待結果 |
|---|--------|------|----------|
| 1 | 登記インポート削除 | 登記インポートを削除 | 正常に論理削除される |
| 2 | 築年数計算 | 物件編集→築年数表示 | 正常に表示される |
| 3 | 販売ステータス連動 | 販売中→成約済みに変更→保存 | 公開ステータスが非公開に連動 |
| 4 | 公開前確認連動 | 販売準備→販売中に変更→保存 | 公開ステータスが公開前確認に連動 |

### 攻撃ポイント

| # | 観点 | 確認内容 |
|---|------|----------|
| 5 | べき等性 | 同じ登記インポートを2回削除しても2回目は404エラー |
| 6 | レグレッション | 築年数の計算結果が変わらないこと |
| 7 | レグレッション | ステータス連動が正常動作すること |

---

## テスト環境

- API: `cd ~/my_programing/REA/rea-api && PYTHONPATH=~/my_programing/REA python -m uvicorn app.main:app --reload --port 8005`
- フロント: `cd ~/my_programing/REA/rea-admin && npm run dev`
