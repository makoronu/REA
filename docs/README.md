# 🏢 REA - Real Estate Automation System

> **自動生成日時**: 2025-09-18 07:09:31

## 🎯 システム概要
REAは不動産業務の完全自動化を目指すPythonベースのシステムです。
ホームズ等のポータルサイトからの物件情報自動収集、データベース管理、高速検索を実現します。

## 📂 仕様書ナビゲーション

### ⚡ クイックアクセス
- [🤖 Claude用チャンク](claude_chunks/) - AI連携最適化済み
- [📊 データベース現在構造](01_database/current_structure.md) - 最重要
- [🔌 API Swagger](http://localhost:8005/docs) - 対話的API文書

### 📊 データベース仕様
- [📋 現在の構造](01_database/current_structure.md) - テーブル一覧・統計
- [🗂️ テーブル詳細](01_database/) - 各テーブルの仕様
- **重要**: properties テーブル（294カラム）要分割

### 🔌 API仕様  
- [📋 API概要](02_api/README.md) - エンドポイント・使用方法
- [🎯 Swagger UI](http://localhost:8005/docs) - 対話的API文書
- **ベースURL**: http://localhost:8005

### 🕷️ スクレイパー仕様
- [📋 スクレイパー概要](03_scraper/README.md) - 実行方法・機能
- **対応サイト**: ホームズ（実装済み）、スーモ（予定）

### 📚 共通ライブラリ仕様
- [📋 ライブラリ概要](04_shared/README.md) - 実装済み・将来予定

## 🚀 クイックスタート

### 💻 開発環境起動
```bash
# 1. Docker起動
open -a Docker
sleep 30

# 2. PostgreSQL起動
#cd /Users/yaguchimakoto/my_programing/REA
docker-compose up -d

# 3. Python環境
source venv/bin/activate

# 4. DB接続確認（新システム）
export DATABASE_URL="postgresql://rea_user:rea_password@localhost/real_estate_db"
python shared/database.py

# 5. API起動
#cd rea-api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8005

# 6. 動作確認
open http://localhost:8005/docs
```

### 🔧 スクレイピング実行
```bash
#cd rea-scraper
python -m src.main collect-urls --max-pages 10
python -m src.main process-batch --batch-size 10
```

## 🔗 重要なURL・パス
- **API文書**: http://localhost:8005/docs
- **データベース**: PostgreSQL (localhost:5432)
- **プロジェクト**: /Users/yaguchimakoto/my_programing/REA
- **仮想環境**: /Users/yaguchimakoto/my_programing/REA/venv

## 🤖 Claude連携ガイド

### 質問パターン別推奨チャンク
| 質問内容 | 読み込むファイル |
|----------|------------------|
| 「データベースについて」 | `01_database/current_structure.md` |
| 「APIについて」 | `02_api/README.md` |
| 「スクレイパーについて」 | `03_scraper/README.md` |
| 「共通ライブラリについて」 | `04_shared/README.md` |
| 「画像機能について」 | `claude_chunks/database_chunks/images.md` |
| 「価格機能について」 | `claude_chunks/database_chunks/pricing.md` |

### 効率的な質問方法
```markdown
❌ 悪い例: 「REAについて教えて」
✅ 良い例: 「REAのデータベース構造について、01_database/current_structure.md を確認して質問に答えて」
```

## 📊 システム統計
- **テーブル数**: 32（自動取得）
- **最大テーブル**: properties (294カラム)
- **API エンドポイント**: 複数
- **対応サイト**: ホームズ（稼働中）

## 🎯 開発フェーズ

### ✅ Phase 1: 基盤完成（完了）
- FastAPI基盤構築
- PostgreSQL環境構築
- 基本的な物件管理機能
- **統一DB接続システム**: `shared/database.py` 完成

### 🔄 Phase 2: 現在進行中
- データベース構造分析（進行中）
- テーブル分割計画
- 仕様書ツリー化（進行中）

### 📋 Phase 3: 今後予定
- 管理画面開発（React）
- 自動入稿システム
- WordPress連携

## 🔄 更新情報
この仕様書は自動生成されます。最新情報はコードベースと同期されています。

---
**生成コマンド**: `python scripts/auto_spec_generator/main.py`  
**最終更新**: 2025-09-18 07:09:31  
**DB接続**: shared/database.py 統一システム使用
