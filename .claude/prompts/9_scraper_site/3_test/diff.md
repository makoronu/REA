# 差分テスト

## やること
1. batch.md成功物件3件のキューをpendingに戻し再取得 → updated確認
2. 1件のsale_priceを手動+100万円 → 再取得 → price_history記録確認
3. 消失検知: seen_ids=3件のみで呼び出し → 残りがdisappeared確認
4. テストデータをクリーンアップ

## 完了条件
- [ ] 更新/価格変更/消失が全て正常動作
- [ ] テストデータを復元した

## 次 → ../4_complete/type_check.md
