# 計画立案

## やること
1. 以下を箇条書きで書き出す：
   - 作成するディレクトリ構成
   - 作成するファイル一覧（予定行数つき）
   - 作成するDBテーブル一覧
   - 既存 rea-scraper から移植するファイル
   - 新規作成するファイル
2. 500行超えのファイル計画がないか確認
3. ユーザーに提示する
4. **承認を得るまで次に進まない**

## 出力フォーマット
```
【作業名】: スクレイパー基盤構築
【ディレクトリ構成】:
  market-intelligence/
  ├── mi-api/
  ├── mi-scraper/
  ├── shared/
  ├── scripts/
  └── docs/

【DBテーブル】:
1. master_categories
2. master_options
3. column_labels
4. scraped_properties
5. price_history
6. listing_status_history
7. scrape_sessions
8. scrape_sources

【移植ファイル（rea-scraperから）】:
1. base_scraper.py → 改修して移植
2. scrapers_common.py → URLQueue/RateLimiter部分を移植
3. selenium_manager.py → そのまま移植
4. decorators.py → そのまま移植

【新規作成ファイル】:
1. mi-scraper/src/pipeline/fetcher.py (〜200行)
2. mi-scraper/src/normalizers/price.py (〜100行)
3. ...

このリストで進めてよいですか？
```

## 完了条件
- [ ] ユーザーから承認を得た

## 次の工程
→ ../2_database/ddl.md
