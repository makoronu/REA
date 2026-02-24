# バッチテスト

## やること
10件の物件を一括で取得→パース→正規化→REA変換→DB保存し、
パイプライン全体が正常に動作することを確認する。

## テスト手順

### Step 1: URL収集（3ページ分）
```bash
python -m mi_scraper collect-urls --site {site_name} --max-pages 3
python -m mi_scraper queue-stats --site {site_name}
```
期待: URLQueue に数十件のURLが追加される

### Step 2: バッチ処理（10件）
```bash
python -m mi_scraper process-batch --site {site_name} --batch-size 10 --save
```
期待: 10件が scraped_properties に INSERT される

### Step 3: DB確認
```sql
-- 件数確認
SELECT COUNT(*) FROM scraped_properties
WHERE source_site = '{site_name}' AND deleted_at IS NULL;

-- データ確認（主要フィールド）
SELECT
    listing_id,
    property_name,
    sale_price,
    prefecture,
    city,
    land_area,
    use_district,
    building_structure,
    listing_status,
    first_seen_at
FROM scraped_properties
WHERE source_site = '{site_name}'
ORDER BY id DESC
LIMIT 10;

-- NULL率確認（取得できていないフィールドの割合）
SELECT
    COUNT(*) AS total,
    COUNT(sale_price) AS has_price,
    COUNT(land_area) AS has_land_area,
    COUNT(use_district) AS has_use_district,
    COUNT(building_structure) AS has_structure,
    COUNT(construction_date) AS has_construction
FROM scraped_properties
WHERE source_site = '{site_name}';
```

### Step 4: セッション統計確認
```sql
SELECT * FROM scrape_sessions
WHERE source_site = '{site_name}'
ORDER BY id DESC LIMIT 1;
```
期待: properties_new = 10, errors = 0

## 確認チェックリスト
- [ ] 10件全て DB に保存されている
- [ ] sale_price が全件で取得できている（最重要フィールド）
- [ ] address 情報が全件で取得できている
- [ ] listing_id が全件でユニーク
- [ ] first_seen_at / last_seen_at が設定されている
- [ ] listing_status = 'active'
- [ ] scrape_sessions にセッションが記録されている
- [ ] レート制限が効いている（処理時間 30秒以上 = 3秒×10件）
- [ ] エラーログに異常がない

## 異常時の対応
- 0件保存 → パーサーが None を返している → unit.md に戻る
- NULL 率が高い → セレクタが合っていない → selectors.md に戻る
- DB エラー → 型不一致の可能性 → converter.md を確認

## 完了条件
- [ ] 10件が正常に DB 保存された
- [ ] 主要フィールドの NULL 率が許容範囲内
- [ ] セッション統計が正しい

## 次の工程
→ diff.md
