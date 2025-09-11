# .env設定について

DB接続設定はプロジェクトルートの.envファイルで一元管理されています。

プロジェクトルート: /Users/yaguchimakoto/my_programing/REA/.env

各モジュールはshared/database.pyを通じて自動的に正しい設定を読み込みます。
