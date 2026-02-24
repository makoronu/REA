# URL発見（Discovery）

## やること
一覧ページを巡回して物件詳細ページのURLリストを収集するロジックを実装する。

## 実装ファイル
```
mi-scraper/src/scrapers/{site_name}/{site_name}_scraper.py
```

## 実装内容

### collect_urls() メソッド
```python
def collect_urls(self, base_url: str, max_pages: int = 50) -> int:
    """
    検索結果ページを巡回して物件URLを収集する。

    1. base_url（1ページ目）にアクセス
    2. 物件カードからリンクを抽出 → URLQueue に追加
    3. 「次へ」リンクから次ページURLを取得
    4. 終了条件まで繰り返し

    Returns: 新規URL件数
    """
```

### 使用する共通基盤
- `fetcher.fetch()` — HTML取得（レート制限付き）
- `URLQueue.add_urls()` — URL追加（重複チェック付き）
- `selectors.py` — CSSセレクタ定義（1_survey で確定済み）

### 注意点
- ページネーション方式は `pagination.md` で確定済みのパターンを使う
- URL正規化（相対URL→絶対URL）
- listing_id の抽出ロジック（URLパスから or ページ内要素から）
- 終了判定（次へなし / 0件 / max_pages）

## テスト
```bash
# 3ページ分だけ試行
python -m mi_scraper collect-urls --site {site_name} --max-pages 3 --dry-run
```

## 完了条件
- [ ] 3ページ分のURL収集が動作する
- [ ] URLQueue にURLが追加される
- [ ] 重複URLが弾かれる
- [ ] レート制限が効いている（3〜8秒間隔）
- [ ] 終了条件で正しく停止する

## 次の工程
→ parser.md
