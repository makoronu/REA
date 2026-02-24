# 差分テスト

## やること
同じ物件を2回取得して、差分検知（更新・消失・価格変更）が正しく動作するか確認する。

## テスト手順

### Step 1: 1回目の取得（batch.md で完了済み）
```sql
-- 現在の状態を確認
SELECT id, listing_id, sale_price, last_seen_at, listing_status
FROM scraped_properties
WHERE source_site = '{site_name}'
ORDER BY id DESC LIMIT 10;
```

### Step 2: 2回目の取得（同じバッチを再実行）
```bash
# URLQueue をリセットして再取得
python -m mi_scraper process-batch --site {site_name} --batch-size 10 --save
```

### Step 3: 更新検知の確認
```sql
-- last_seen_at が更新されているか
SELECT id, listing_id, last_seen_at, updated_at
FROM scraped_properties
WHERE source_site = '{site_name}'
ORDER BY updated_at DESC LIMIT 10;
```
期待: last_seen_at が2回目の実行時刻に更新されている

### Step 4: 価格変更検知の確認（手動シミュレーション）
```sql
-- テスト用: 1件の価格を手動で変更して再取得をシミュレーション
-- （実際にはサイト側で価格が変わるケースのテスト）
UPDATE scraped_properties
SET sale_price = sale_price - 1000000
WHERE source_site = '{site_name}'
AND id = (SELECT MIN(id) FROM scraped_properties WHERE source_site = '{site_name}');

-- 再取得後に price_history を確認
SELECT ph.*, sp.listing_id
FROM price_history ph
JOIN scraped_properties sp ON sp.id = ph.scraped_property_id
WHERE sp.source_site = '{site_name}'
ORDER BY ph.recorded_at DESC;
```
期待: price_history にレコードが追加されている

### Step 5: 消失検知の確認（手動シミュレーション）
```sql
-- テスト用: 1件を「今回の巡回で見つからなかった」状態にする
-- status_tracker.detect_disappeared() を呼び出す

-- 消失後の状態確認
SELECT id, listing_id, listing_status, disappeared_at
FROM scraped_properties
WHERE source_site = '{site_name}'
AND listing_status = 'disappeared';

-- listing_status_history を確認
SELECT lsh.*, sp.listing_id
FROM listing_status_history lsh
JOIN scraped_properties sp ON sp.id = lsh.scraped_property_id
WHERE sp.source_site = '{site_name}'
ORDER BY lsh.detected_at DESC;
```
期待: disappeared_at が設定され、listing_status_history に記録されている

## 確認チェックリスト
- [ ] 2回目取得で既存物件が UPDATE（INSERT重複なし）
- [ ] last_seen_at が更新されている
- [ ] 価格変更時に price_history に記録される
- [ ] 消失検知が動作する（disappeared_at 設定 + 履歴記録）
- [ ] UPSERT の UNIQUE 制約が正しく機能している

## テスト後のクリーンアップ
```sql
-- テストデータ削除（論理削除）
UPDATE scraped_properties
SET deleted_at = NOW()
WHERE source_site = '{site_name}';

-- または物理削除（テスト環境のみ）
-- DELETE FROM price_history WHERE scraped_property_id IN (...);
-- DELETE FROM listing_status_history WHERE scraped_property_id IN (...);
-- DELETE FROM scraped_properties WHERE source_site = '{site_name}';
```

## 完了条件
- [ ] 更新検知が正常動作
- [ ] 価格変更記録が正常動作
- [ ] 消失検知が正常動作
- [ ] テストデータをクリーンアップした

## 次の工程
→ ../4_complete/quality.md
