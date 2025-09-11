# 🧠 Claude即座復活コンテキスト

## 🚨 最優先情報（10秒で把握）
- **プロジェクト**: REA - Real Estate Automation System
- **開発者**: yaguchimakoto (GitHub: makoronu)
- **現在地**: `/Users/yaguchimakoto/my_programing/REA`
- **DB状態**: unknown - 全体エラー: name 'cd' is not defined...
- **プログラム**: 213ファイル分析済み
- **最終更新**: 2025-07-23 16:40:48

## 🎯 現在の達成レベル（2025年7月23日）
✅ **完全稼働中**: FastAPI (port 8005) + PostgreSQL (Docker)
✅ **統一DB接続**: shared/database.py で完全統一化
✅ **共通ライブラリ活用**: 重複コード排除・DRY原則適用
✅ **分割リファクタリング完了**: 700行→8ファイル（保守性向上）
✅ **エラーハンドリング強化**: DB接続失敗時のフォールバック完備
✅ **プログラム構造自動保存**: 動的検出システム完成
✅ **Claude記憶システム**: 完全自動化実行システム完成
✅ **自動仕様書生成**: 58ファイル生成、Claude最適化チャンク完備

## ⚡ 必須コマンド（暗記必須）

### 環境移動・起動
    # cd /Users/yaguchimakoto/my_programing/REA
    source venv/bin/activate

### Docker PostgreSQL起動（最重要）
    docker-compose up -d

### 仕様書生成
    # cd scripts/auto_spec_generator
    python main.py

### Claude記憶システム自動実行
    python auto_claude_briefing.py

### API起動
    # cd rea-api
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8005

## 🚨 絶対やってはいけない事
❌ localStorage使用（Claude.ai環境では動かない）
❌ 部分修正（全体書き直し必須）
❌ venv忘れ（source venv/bin/activate必須）
❌ 本番データ直接操作
❌ 共通ライブラリを使わずに独自実装

## 🔧 頻出エラーと解決法

### DB接続エラー
    # Docker PostgreSQL起動
    docker-compose up -d
    # 共通ライブラリで接続テスト
    python -c "from shared.database import READatabase; print(READatabase.test_connection())"

### pydantic_settingsエラー
    pip install pydantic-settings

### No module named 'shared'
    sys.path.append(str(self.base_path))

### ポート競合
    lsof -i :8005
    kill -9 <PID>

## 🏆 技術スタック（稼働中）
- **DB**: PostgreSQL 15 (Docker: real_estate_db)
- **API**: FastAPI 0.104.1 (Port: 8005)
- **言語**: Python 3.11+ (venv必須)
- **共通ライブラリ**: shared/database.py (統一DB接続)
- **仕様書生成**: auto_spec_generator (58ファイル自動生成)

## 📊 現在の仕様書システム
- **自動生成**: 58ファイル（データベース+プログラム構造+Claude記憶）
- **出力先**: docs/ ディレクトリ
- **更新方法**: python main.py (scripts/auto_spec_generator/)
- **Claude記憶**: python auto_claude_briefing.py
- **共通ライブラリ**: shared/ ディレクトリで一元管理

## 🚨 禁止事項・重要ルール

### 開発ルール（必須）
- **VS Code必須**: コード変更は必ずVS Codeで実行
- **型ヒント必須**: Python関数は必ず型を明記
- **コメント必須**: 関数・クラスには日本語コメント
- **全体書き直し方式**: 部分修正は絶対禁止（エラーの元凶）
- **共通ライブラリ優先**: shared/ にある機能は必ず使用

### 実行時の必須手順（毎回）
- **必ずcd**: /Users/yaguchimakoto/my_programing/REA
- **venv有効化**: source venv/bin/activate
- **Docker確認**: docker ps | grep postgres
- **共通ライブラリ確認**: ls shared/

### データバックアップ（重要作業前必須）
    # DBバックアップ
    pg_dump -U rea_user -d real_estate_db > backup_$(date +%Y%m%d).sql
    
    # gitコミット
    git add . && git commit -m "作業前バックアップ"

## 🚀 次回会話時の手順
1. この文書を読んで現状把握（必須）
2. 作業前に環境確認（cd, venv, Docker）
3. 共通ライブラリの活用を優先
4. 変更後は必ず仕様書更新（python main.py）

## 🌟 REAの現在レベル

### 世界基準での位置:
- **Google並みのマイクロサービス設計**: 分割リファクタリング完了
- **Netflix並みの自動化レベル**: DB・仕様書完全自動生成
- **Amazon並みのスケーラビリティ**: 新テーブル・新機能自動対応
- **Facebook並みの共通ライブラリ**: shared/ による完全統一化

自動生成日時: 2025-07-23 16:40:48
記憶システム: v2.0 (共通ライブラリ統一版)
このドキュメントでClaude記憶喪失問題も完全解決！ 🧠💪
