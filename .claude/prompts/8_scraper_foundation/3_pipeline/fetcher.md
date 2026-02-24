# HTTP取得基盤（Fetcher）

## 前提
- **Seleniumヘッドレスをデフォルトとせよ**（不動産ポータルはボットガード前提）
- requests は robots.txt取得等の軽量リクエストのみ
- ボットガード突破: User-Agent偽装、Cookie保持、JS実行待ち、ランダム遅延

## やること
1. fetcher.py: HTML取得（Selenium主体、リトライ、生HTML保存）
2. rate_limiter.py: ランダム待機（3〜8秒）
3. robots_checker.py: robots.txt取得・パース・Disallow判定
4. block_detector.py: 403/429/202/CAPTCHA検知→自動停止
5. **実際に対象サイトからHTML取得できることをSeleniumで検証**

## ルール
- ヘッダー擬態（User-Agent等）は定数ファイルで管理
- 連続5回失敗で自動停止→通知
- Selenium WebDriverは使い回し（毎回起動しない）

## 完了条件
- [ ] Seleniumで対象サイトのHTMLが取得できることを実証した
- [ ] レート制限・robots.txt・ブロック検知が動作する
- [ ] 全ファイル500行以下

## 次 → normalizers.md
