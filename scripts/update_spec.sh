#!/bin/bash
echo "🚀 REA仕様書を更新します..."

cd /Users/yaguchimakoto/my_programing/REA

# Python環境有効化
source venv/bin/activate

# 必要なパッケージ確認
pip install psycopg2-binary requests > /dev/null 2>&1

# 仕様書生成
python scripts/spec_generator/generate_claude_context.py

# 結果確認
echo ""
echo "✅ 完了！"
echo ""

# Finderで開くコマンドをクリップボードにコピー
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "open /Users/yaguchimakoto/my_programing/REA/docs/claude_specs/" | pbcopy
    echo "📋 以下のコマンドがクリップボードにコピーされました:"
    echo "👉 open /Users/yaguchimakoto/my_programing/REA/docs/claude_specs/"
    echo ""
    echo "ターミナルで Cmd+V して実行すると、Finderが開きます"
    echo "latest.md をClaude.aiにドラッグ&ドロップしてください"
fi