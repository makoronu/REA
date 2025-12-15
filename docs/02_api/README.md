# 🔌 REA API仕様

## 📋 概要
- **生成日時**: 2025-09-18 07:09:31
- **ベースURL**: http://localhost:8005
- **プロジェクト**: rea-api
- **フレームワーク**: FastAPI

## 🎯 エンドポイントファイル
- **検出数**: 2
- **ファイル一覧**:
  - `properties.py`
  - `metadata.py`

## 🔌 主要エンドポイント

### 物件API
- `GET /api/v1/properties/` - 物件一覧取得
- `POST /api/v1/properties/` - 物件作成
- `GET /api/v1/properties/{id}` - 物件詳細取得
- `PUT /api/v1/properties/{id}` - 物件更新
- `DELETE /api/v1/properties/{id}` - 物件削除

### ZOHO CRM連携API
- `GET /api/v1/zoho/status` - ZOHO接続状態確認
- `GET /api/v1/zoho/auth` - OAuth認証URL取得
- `GET /api/v1/zoho/callback` - OAuthコールバック
- `GET /api/v1/zoho/properties` - ZOHOから物件一覧取得
- `POST /api/v1/zoho/import` - ZOHO→REA インポート
- `POST /api/v1/zoho/sync` - REA→ZOHO 同期（複数物件）
- `POST /api/v1/zoho/sync/{property_id}` - REA→ZOHO 同期（単一物件）

### ZOHO同期の仕組み

**インポート（ZOHO→REA）**
1. `zoho_client.get_record()` でZOHOからデータ取得
2. `zoho_mapper.map_record()` でREA形式に変換（DBのimport_field_mappings, import_value_mappingsを参照）
3. properties, land_info, building_infoテーブルに保存

**エクスポート（REA→ZOHO）**
1. `_get_property_full_data()` でREAから物件データ取得
2. `zoho_reverse_mapper.reverse_map_record()` でZOHO形式に変換（逆マッピング）
3. `zoho_client.update_record()` または `create_record()` でZOHOに送信

**マッピング管理テーブル**
- `import_field_mappings`: フィールド対応（source_field → target_column）
- `import_value_mappings`: 値変換（例: "木造" → "1:木造"）
- `master_options`: REA側の選択肢定義

## 📚 API文書
- **Swagger UI**: http://localhost:8005/docs
- **ReDoc**: http://localhost:8005/redoc

## 🔧 開発環境
- **ポート**: 8005
- **起動コマンド**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8005`
- **開発サーバー**: uvicorn + reload

## 🏗️ プロジェクト構造
```
rea-api/
├── app/
│   ├── main.py              # FastAPIアプリケーション
│   ├── api/                 # APIルーティング
│   ├── core/                # 設定・DB接続
│   ├── models/              # SQLAlchemyモデル
│   ├── schemas/             # Pydanticスキーマ
│   └── crud/                # CRUD操作
├── requirements.txt         # 依存関係
└── .env                     # 環境変数
```

## 🤖 DB接続統一対応
- **従来**: 個別のDB接続処理
- **新方式**: `shared/database.py` 使用推奨
- **接続確認**: `python shared/database.py`

## 🤖 使用例
```bash
# API起動
#cd rea-api
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8005

# 動作確認
curl http://localhost:8005/api/v1/properties/
```
