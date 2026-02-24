# robots.txt 確認

## やること
1. 対象サイトの robots.txt を取得する
2. Disallow パスを一覧化する
3. Crawl-delay の有無を確認する
4. スクレイピング対象URL（検索結果ページ・物件詳細ページ）が Disallow に該当しないか確認する

## 確認手順
```bash
# robots.txt取得
curl -s https://{site_domain}/robots.txt
```

## 記録フォーマット
```
【サイト】: {サイト名}
【robots.txt URL】: https://{domain}/robots.txt
【Crawl-delay】: {秒数 or なし}
【Disallow一覧】:
  - /path1/
  - /path2/

【スクレイピング対象URLの判定】:
  - 検索結果ページ: {URL} → 許可 / 禁止
  - 物件詳細ページ: {URL} → 許可 / 禁止
```

## 停止条件
- 物件詳細ページが Disallow に該当する → **即停止** → ユーザーに報告
- 検索結果ページが Disallow に該当する → **即停止** → ユーザーに報告

## 完了条件
- [ ] robots.txt を確認した
- [ ] Disallow パスを一覧化した
- [ ] 対象URLが許可されていることを確認した
- [ ] Crawl-delay を RateLimiter 設定に反映した

## 次の工程
→ html_analysis.md
