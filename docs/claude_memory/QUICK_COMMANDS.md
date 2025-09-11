# ⚡ REA クイックコマンド集

## 🚀 最頻用コマンド

### 全環境起動（最重要）
    # cd /Users/yaguchimakoto/my_programing/REA
    source venv/bin/activate
    docker-compose up -d
    # cd scripts/auto_spec_generator && python main.py

### Claude記憶システム自動実行
    python auto_claude_briefing.py

### API起動
    # cd rea-api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8005

## 🔧 トラブル対応

### DB接続確認（共通ライブラリ使用）
    python -c "from shared.database import READatabase; print(READatabase.test_connection())"
    python -c "from shared.database import READatabase; print(READatabase.get_all_tables())"

### ポート確認・解放
    lsof -i :8005
    docker ps | grep postgres

### venv確認
    which python
    pip list | grep fastapi

## 🚨 エラー時の対処
- **DB接続エラー**: ⚠️ 警告表示でシステム継続
- **フォールバック**: 既知情報での仕様書生成
- **エラーログ**: 詳細な解決手順を表示
- **共通ライブラリ**: shared/database.py でエラー処理統一
