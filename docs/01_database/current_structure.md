# データベース接続エラー

エラー: DB接続失敗
発生時刻: 2025-09-18 07:09:31

## 対処方法

1. Docker PostgreSQL起動
   ```
   docker-compose up -d
   ```

2. 接続テスト
   プロジェクトルートで実行:
   ```
   python -c "from shared.database import READatabase; print(READatabase.test_connection())"
   ```

3. 環境変数確認
   ```
   echo $DATABASE_URL
   ```
