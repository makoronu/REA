# robots.txt確認

## やること
1. 対象サイトのrobots.txtを取得
2. Disallowパスを一覧化
3. Crawl-delayの有無を確認
4. スクレイピング対象URL（検索結果/物件詳細）がDisallowに該当しないか確認

## 停止条件
- 対象URLがDisallowに該当 → **即停止** → ユーザーに報告

## 完了条件
- [ ] 対象URLが許可されていることを確認した
- [ ] Crawl-delayをRateLimiter設定に反映した

## 次 → html_analysis.md
