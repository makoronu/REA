# サイト固有フェッチャー設定

## やること
1. scraper.pyに`_setup_fetcher(fetcher)`関数を実装
2. html_analysis.mdで発見したサイト固有の設定を集約

## 検討項目（該当する場合のみ）
- Refererヘッダー + セッションリセット後の復元（`_reset_session`モンキーパッチ）
- robots.txtキャッシュ注入（ContaboIPブロック時）
- Cookie/セッション管理（WAFチャレンジ等）

## ルール
- 共通基盤（fetcher.py等）を改変しない
- `_setup_fetcher()`はscraper.py内に閉じ込める
- `collect_urls()`と`process_batch()`の冒頭で呼ぶ
- URL定数はselectors.pyの`BASE_URL`を参照

## 完了条件
- [ ] `_setup_fetcher()`を実装した
- [ ] 1件の詳細ページ取得成功を確認した

## 次 → discovery.md
