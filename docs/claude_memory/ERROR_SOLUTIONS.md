# 🔧 REA エラー解決ガイド

## 🚨 現在のDB状態
- **状態**: unknown
- **エラー情報**: 全体エラー: name 'cd' is not defined
- **接続方式**: shared/database.py（共通ライブラリ）

## 💡 解決手順

### DB接続エラーの場合

1. Docker PostgreSQL起動確認
    docker ps | grep postgres
    docker-compose up -d

2. 環境変数設定
    export DATABASE_URL="postgresql://rea_user:rea_password@localhost/real_estate_db"

3. shared/database.py で接続テスト
    # cd /Users/yaguchimakoto/my_programing/REA
    python -c "from shared.database import READatabase; print(READatabase.test_connection())"

4. shared/database.py 確認
    code shared/database.py
    # 認証情報確認: rea_user, rea_password

### システム継続方法
- **仕様書生成**: DB接続失敗でも継続実行
- **フォールバック**: 既知情報で代替表示
- **エラーログ**: 詳細情報で問題特定
- **共通ライブラリ**: すべてのDB操作はshared/database.py経由

更新日時: 2025-07-23 16:40:48
