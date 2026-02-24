# HTTP取得基盤（Fetcher）

## やること
1. fetcher.py: HTML取得（Selenium/requests切替、リトライ、生HTML保存）
2. rate_limiter.py: ランダム待機（3〜8秒）、scrapers_common.pyから移植
3. robots_checker.py: robots.txt取得・パース・Disallow判定
4. block_detector.py: 403/429/CAPTCHA検知→自動停止

## ルール
- ヘッダー擬態（User-Agent等）は定数ファイルで管理
- 連続5回失敗で自動停止→通知

## 完了条件
- [ ] URLを渡してHTMLが返る
- [ ] レート制限・robots.txt・ブロック検知が動作する
- [ ] 全ファイル500行以下

## 次 → normalizers.md
