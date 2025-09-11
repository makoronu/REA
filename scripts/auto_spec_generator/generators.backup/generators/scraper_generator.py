# generators/scraper_generator.py
from pathlib import Path
from typing import Any, Dict

from .base_generator import BaseGenerator


class ScraperGenerator(BaseGenerator):
    """スクレイパー仕様生成クラス"""

    def generate(self) -> Dict[str, Any]:
        """スクレイパー仕様生成"""
        scraper_path = self.base_path / "rea-scraper"

        if not scraper_path.exists():
            self.print_status("⚠️ rea-scraperディレクトリが見つかりません")
            return {}

        # スクレイパーファイルをスキャン
        scrapers_dir = scraper_path / "src" / "scrapers"
        scraper_files = []

        if scrapers_dir.exists():
            scraper_files = list(scrapers_dir.rglob("*.py"))
            scraper_files = [f for f in scraper_files if f.name != "__init__.py"]

        # スクレイパー概要生成
        content = f"""# 🕷️ REA スクレイパー仕様

## 📋 概要
- **生成日時**: {self.get_timestamp()}
- **対象サイト**: ホームズ（実装済み）
- **プロジェクト**: rea-scraper
- **検出ファイル数**: {len(scraper_files)}

## 🎯 主要機能
- **URL収集**: 物件一覧ページから物件URLを収集
- **詳細抽出**: 各物件ページから詳細情報を抽出
- **画像ダウンロード**: 物件画像の自動ダウンロード
- **データ保存**: PostgreSQLに自動保存

## 🏗️ プロジェクト構造
```
rea-scraper/
├── src/
│   ├── main.py              # メインエントリーポイント
│   ├── scrapers/            # サイト別スクレイパー
│   │   ├── base/            # 基底クラス
│   │   └── homes/           # ホームズ対応
│   ├── utils/               # ユーティリティ
│   │   ├── selenium_manager.py
│   │   ├── logger.py
│   │   └── process_manager.py
│   └── config/              # 設定管理
├── data/                    # データ保存先
├── logs/                    # ログファイル
└── requirements.txt         # 依存関係
```

## 🔧 実行方法

### URL収集
```bash
#cd rea-scraper
source ../venv/bin/activate
python -m src.main collect-urls --max-pages 10
```

### バッチ処理
```bash
python -m src.main process-batch --batch-size 10 --show-sample
```

### 全自動処理
```bash
python -m src.main process-all --batch-size 10 --interval 300 --save
```

### 統計確認
```bash
python -m src.main queue-stats
```

## 🛠️ 主要クラス
- **HomesPropertyScraper**: ホームズ専用スクレイパー
- **SeleniumManager**: ブラウザ制御・Bot対策
- **URLQueue**: URL管理・永続化
- **DatabaseSaver**: データベース保存

## 📊 パフォーマンス
- **処理速度**: 約11秒/物件
- **成功率**: 100%（テスト実行分）
- **収集実績**: 279URL（96件有効）

## 🤖 DB接続統一対応
- **従来**: 個別のDB接続処理
- **新方式**: `shared/database.py` 使用推奨
- **接続確認**: `python shared/database.py`

## 🤖 使用例
```bash
# 環境起動
#cd /Users/yaguchimakoto/my_programing/REA
source venv/bin/activate
#cd rea-scraper

# 対話型実行
./scripts/start_scraping.sh

# バックグラウンド実行
nohup ./scripts/monitor_scraper.sh > logs/monitor.log 2>&1 &
```
"""

        # ファイル保存
        scraper_dir = self.get_output_dir("03_scraper")
        self.save_content(content, scraper_dir / "README.md")

        self.print_status("✅ スクレイパー仕様生成完了")
        return {"scraper_path": str(scraper_path), "scraper_files": len(scraper_files)}
