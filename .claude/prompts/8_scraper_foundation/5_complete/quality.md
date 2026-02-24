# 品質チェック

## チェックリスト
- [ ] 全ファイル500行以下（`wc -l`で確認）
- [ ] ハードコードなし
- [ ] ENUM なし
- [ ] 全テーブルにdeleted_at
- [ ] 全SELECTにdeleted_at IS NULL
- [ ] パラメータバインディング
- [ ] エラー握りつぶしなし
- [ ] datetime UTC統一

## 中断条件
- 1つでもNG → 修正してから次へ

## 次 → schema_update.md
