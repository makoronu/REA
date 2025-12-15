# 🕷️ REA スクレイパー仕様

## 📋 概要
- **生成日時**: 2025-09-18 07:09:31
- **対象サイト**: ホームズ（実装済み）
- **プロジェクト**: rea-scraper
- **検出ファイル数**: 29

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

---

## 📦 メタデータ駆動インポートシステム

### 概要

スクレイピングしたデータをREAにインポートする際、**メタデータ駆動マッピング**を使用する。
コードにハードコーディングせず、DBテーブルでマッピングルールを管理する。

### テーブル構造

| テーブル | 役割 |
|---------|------|
| `import_field_mappings` | ソースフィールド → REAカラムの対応 |
| `import_value_mappings` | 値の変換ルール（例: "木造" → "1:木造"） |
| `master_options` | REAの選択肢定義（code → label） |

### 使い方

```python
from app.services.zoho.mapper import MetaDrivenMapper

# source_type を変えるだけで他サイトに対応
mapper = MetaDrivenMapper(source_type="suumo")  # or "homes", "athome"
result = mapper.map_record(scraped_data)

# 結果
# {
#   "properties": {"property_type": "1", "price": 1500, ...},
#   "land_info": {"land_area": 200.5, "use_district": "5", ...},
#   "building_info": {"building_structure": "1", ...},
#   "amenities": {...}
# }
```

### 新しいサイト対応手順

1. **import_value_mappingsにマッピング追加**
   ```sql
   INSERT INTO import_value_mappings (source_type, field_name, source_value, target_value)
   VALUES
     ('suumo', 'building_structure', '木造', '1:木造'),
     ('suumo', 'building_structure', '鉄骨', '3:鉄骨造'),
     ('suumo', 'building_structure', '', '0:未設定');
   ```

2. **import_field_mappingsにフィールド対応追加**
   ```sql
   INSERT INTO import_field_mappings (source_type, source_field, target_table, target_column, transform_type)
   VALUES
     ('suumo', 'tatemono_kouzou', 'building_info', 'building_structure', 'value_map'),
     ('suumo', 'kakaku', 'properties', 'price', 'numeric');
   ```

3. **Mapperを使ってインポート**
   ```python
   mapper = MetaDrivenMapper(source_type="suumo")
   for item in scraped_items:
       result = mapper.map_record(item)
       # DBに保存
   ```

### 重要なルール

- **空文字/NULLの処理**: `import_value_mappings`に空文字→0:未設定のマッピングを必ず登録
- **master_optionsとの整合性**: target_valueのcodeはmaster_optionsに存在すること
- **ハードコーディング禁止**: 変換ルールは全てDBで管理
