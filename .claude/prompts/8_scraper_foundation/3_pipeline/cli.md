# CLIエントリーポイント

## やること
1. mi-scraper/src/main.py を作成
2. コマンド: collect-urls / process-batch / queue-stats / fetch-one
3. 引数: --site / --max-pages / --batch-size / --save / --dry-run

## ルール
- 全サイトで共通のCLI。--siteで切り替え
- 各コマンドがパイプライン（fetcher→parser→normalizer→converter→registrar）を呼ぶ

## 完了条件
- [ ] --help が動作する
- [ ] collect-urls / process-batch が動作する

## 次 → scheduler.md
