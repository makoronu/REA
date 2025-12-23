# スキーマ確認

## やること
1. 変更対象テーブルを特定
2. column_labelsからスキーマ取得
3. 型・必須・バリデーション確認
4. **カラム追加時: column_labelsテーブル構造を確認**

## 確認コマンド
```bash
# データテーブルのカラム確認
ssh rea-conoha "sudo -u postgres psql real_estate_db -c \"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '[対象テーブル]'\""

# column_labelsのカラム構造確認（カラム追加時は必須）
ssh rea-conoha "sudo -u postgres psql real_estate_db -c \"SELECT column_name FROM information_schema.columns WHERE table_name = 'column_labels'\""
```

## column_labelsの正しいカラム名（注意）
- japanese_label（label_jaではない）
- group_name（field_groupではない）
- visible_for（ARRAY型）

## 完了条件
- [ ] 対象カラムの型を確認した
- [ ] バリデーションルールを確認した
- [ ] カラム追加時: column_labels構造を確認した

## 中断条件
- スキーマにないカラム → 停止して確認

## 次の工程
→ existing.md
