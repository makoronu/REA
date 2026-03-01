# 差分テスト

## やること

### Step 1: 再取得テスト（updated確認）
1. batch.mdで成功した物件3件のキューをpendingに戻す
```sql
UPDATE url_queue
SET status = 'pending', updated_at = NOW()
WHERE source_id = {source_id}
AND listing_id IN ('{id1}', '{id2}', '{id3}')
```
2. `process_batch(fetcher, source_id, batch_size=3)` を実行
3. 結果が `updated` であること（insertedではない）を確認

### Step 2: 価格変更テスト（price_history確認）
1. 成功した物件1件のsale_priceを手動で+100万円に変更
```sql
UPDATE scraped_properties
SET sale_price = sale_price + 1000000
WHERE listing_id = '{id}' AND source_site = '{site}'
```
2. キューをpendingに戻して`process_batch`を実行
3. price_historyにレコードが記録されたことを確認

### Step 3: 消失検知テスト
1. `detect_disappeared(source_site, seen_ids)` を呼び出し
   - seen_ids = 成功した3件のみ
2. 残りの物件がdisappearedになることを確認

### Step 4: クリーンアップ
1. disappeared_atをNULLに戻す
2. listing_statusをactiveに戻す

## 確認項目
- [ ] 2回目でUPDATE（INSERT重複なし）
- [ ] last_seen_atが更新されている
- [ ] 価格変更時にprice_historyに記録される
- [ ] 消失検知が動作する
- [ ] テストデータをクリーンアップした

## 完了条件
- [ ] 更新/価格変更/消失が全て正常動作

## 次 → ../4_complete/type_check.md
