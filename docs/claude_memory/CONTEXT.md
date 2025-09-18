# REAプロジェクトコンテキスト

更新日時: 2025-09-18 07:09:31
プロジェクトパス: /Users/yaguchimakoto/my_programing/REA

## 現在の状態

- データベース: disconnected (0テーブル)
- プログラムファイル: 165ファイル
- API: FastAPI (port 8005)
- DB: PostgreSQL (Docker: real_estate_db)

## 必須コマンド

### 環境起動
```bash
# プロジェクトルートで実行
source venv/bin/activate
docker-compose up -d
```

### 仕様書生成
```bash
# scripts/auto_spec_generatorディレクトリで実行
python main.py
```

### API起動
```bash
# rea-apiディレクトリで実行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
```

## トラブルシューティング

### DB接続エラー
```bash
docker ps | grep postgres
docker-compose up -d
```

### ポート競合
```bash
lsof -i :8005
kill -9 <PID>
```

### モジュールエラー
```bash
pip install -r requirements.txt
```

## 現在のエラー
- DB接続失敗


## プロジェクト構造

- `rea-api/`: FastAPIバックエンド
- `rea-scraper/`: スクレイピングモジュール
- `shared/`: 共通ライブラリ
- `scripts/auto_spec_generator/`: 仕様書生成システム

## 共通ライブラリ

- `shared/database.py`: DB接続統一
- `shared/config.py`: 設定管理
- `shared/logger.py`: ログ管理
