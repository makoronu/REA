# 準備

## やること
1. マイグレーションファイル確認（破壊的変更なし）
2. マイグレーション実行（DB変更ある場合）
3. git push

## マイグレーション実行
```bash
cat scripts/migrations/XXX.sql | ssh rea-conoha "sudo -u postgres psql real_estate_db"
```

## 禁止
- DROP TABLE / DROP COLUMN
- TRUNCATE / DELETE

## 完了条件
- [ ] マイグレーション実行済み（該当時）
- [ ] git push済み

## 次 → 2_execute.md
