# 🤖 Claude専用：REA API情報

## 🔌 重要な事実
- **URL**: http://localhost:8005
- **フレームワーク**: FastAPI
- **ドキュメント**: http://localhost:8005/docs
- **起動**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8005`

## 📋 主要エンドポイント
- `GET /api/v1/properties/` - 物件一覧
- `POST /api/v1/properties/` - 物件作成
- `GET /api/v1/properties/{id}` - 物件詳細

## 🔧 DB接続統一化対応
- **推奨**: shared/database.py 使用
- **利点**: 接続エラー撲滅、統一性確保

## 💡 開発時の注意
- ポート8005で起動
- Swagger UIで動作確認
- PostgreSQL接続必須
- 環境変数設定: `export DATABASE_URL="postgresql://rea_user:rea_password@localhost/real_estate_db"`
