# HTTP取得基盤（Fetcher）

## やること
共通取得レイヤーを実装する。全サイト共通で使う。

## 作成ファイル
```
mi-scraper/src/pipeline/fetcher.py    (〜200行)
mi-scraper/src/utils/rate_limiter.py  (〜80行)  ← scrapers_common.pyから移植
mi-scraper/src/utils/robots_checker.py (〜100行)
mi-scraper/src/utils/block_detector.py (〜100行)
mi-scraper/src/utils/proxy_manager.py  (〜80行)  ← Phase 2で本格実装、スタブのみ
```

## fetcher.py の責務
1. HTTP GET でHTMLを取得
2. Selenium / requests の切り替え（サイト設定で制御）
3. レート制限（RateLimiter呼び出し）
4. robots.txt チェック（RobotsChecker呼び出し）
5. ブロック検知（BlockDetector呼び出し）
6. リトライ（exponential backoff、最大3回）
7. 生HTML保存（storage/{site}/{yyyy-mm}/{listing_id}_{date}.html）
8. セッション維持（Cookie）

## rate_limiter.py の仕様
- 既存 scrapers_common.py の RateLimiter をベースに移植
- min_delay / max_delay をサイトごとに設定可能
- random.uniform でランダム待機
- 開始時刻のランダム化（±30分）

## robots_checker.py の仕様
- 起動時に robots.txt を取得・パース
- Disallow パスを巡回対象から除外
- Crawl-delay があれば rate_limiter に反映
- 24時間ごとに再取得

## block_detector.py の仕様
- HTTP 403/429/503 検知
- CAPTCHA 要素検知（レスポンスHTML内の特定パターン）
- 物件HTMLとの内容差異検知（正常時のHTMLサイズと比較）
- 連続N回失敗で自動停止 → 通知

## ヘッダー擬態
```python
DEFAULT_HEADERS = {
    "User-Agent": "（実在Chrome最新版の文字列）",
    "Accept": "text/html,application/xhtml+xml,...",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}
```
※ User-Agent はハードコードせず定数ファイルで管理

## 完了条件
- [ ] fetcher.py が単体で動作する（URLを渡してHTMLが返る）
- [ ] レート制限が効いている（3〜8秒間隔）
- [ ] robots.txt チェックが動作する
- [ ] ブロック検知が動作する（403返却時に停止）
- [ ] 生HTML保存が動作する
- [ ] 全ファイル500行以下

## 次の工程
→ normalizers.md
