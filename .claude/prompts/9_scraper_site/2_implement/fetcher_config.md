# サイト固有フェッチャー設定

## やること
1. scraper.pyに`_setup_fetcher(fetcher)`関数を実装
2. html_analysis.mdで発見したサイト固有の設定を集約

## 検討項目（該当する場合のみ実装）

### ヘッダー設定
- Refererヘッダー（502/403防止に必要なサイトあり）
- セッションリセット後のヘッダー復元（`_reset_session`のモンキーパッチ）

### robots.txt回避
- ContaboIPからrobots.txt直接取得がブロックされる場合
- 事前調査済みrobots.txt内容を`_ROBOTS_TXT`定数として保持
- `fetcher.robots_checker._cache`にキャッシュ注入

### Cookie/セッション管理
- 初回アクセスでCookie取得が必要な場合
- WAFチャレンジ通過後のセッション維持

## パターン

```python
def _setup_fetcher(fetcher):
    """サイト固有のfetcher設定（scraper.py内に配置）"""
    # 1. ヘッダー設定
    fetcher._session.headers["Referer"] = BASE_URL + "/"

    if not getattr(fetcher, "_{site}_patched", False):
        # 2. セッションリセット後もヘッダー復元
        original_reset = fetcher._reset_session
        def _reset_with_headers():
            original_reset()
            fetcher._session.headers["Referer"] = BASE_URL + "/"
        fetcher._reset_session = _reset_with_headers

        # 3. robots.txtキャッシュ注入（必要な場合のみ）
        # ...

        fetcher._{site}_patched = True
```

## ルール
- 共通基盤（fetcher.py等）を改変しない
- サイト固有の設定はscraper.pyの`_setup_fetcher()`に閉じ込める
- `collect_urls()`と`process_batch()`の冒頭で`_setup_fetcher(fetcher)`を呼ぶ
- URL定数はselectors.pyの`BASE_URL`を参照（ハードコード禁止）

## 完了条件
- [ ] `_setup_fetcher()`を実装した（該当項目のみ）
- [ ] フェッチ成功を確認した（1件の詳細ページ取得テスト）

## 次 → discovery.md
