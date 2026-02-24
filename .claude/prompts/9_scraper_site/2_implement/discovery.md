# URL発見（Discovery）

## やること
1. {site_name}_scraper.pyにcollect_urls()を実装
2. 一覧ページ巡回→物件詳細URLを抽出→URLQueueに追加
3. pagination.mdで確定したパターンを使用

## ルール
- fetcher.fetch()で取得（レート制限付き）
- URL正規化（相対→絶対）
- selectors.pyのセレクタを使用

## 完了条件
- [ ] 3ページ分のURL収集が動作する
- [ ] 重複URLが弾かれる
- [ ] レート制限が効いている

## 次 → parser.md
