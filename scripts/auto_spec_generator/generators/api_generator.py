# generators/api_generator.py
from pathlib import Path
from typing import Dict, Any
from .base_generator import BaseGenerator

class APIGenerator(BaseGenerator):
    """API仕様生成クラス"""
    
    def generate(self) -> Dict[str, Any]:
        """API仕様生成"""
        api_path = self.base_path / "rea-api"
        
        if not api_path.exists():
            self.print_status("⚠️ rea-apiディレクトリが見つかりません")
            return {}
        
        # FastAPIファイルをスキャン
        endpoints_dir = api_path / "app" / "api" / "api_v1" / "endpoints"
        endpoint_files = []
        
        if endpoints_dir.exists():
            endpoint_files = list(endpoints_dir.glob("*.py"))
            endpoint_files = [f for f in endpoint_files if f.name != "__init__.py"]
        
        # API概要生成
        content = f"""# 🔌 REA API仕様

## 📋 概要
- **生成日時**: {self.get_timestamp()}
- **ベースURL**: http://localhost:8005
- **プロジェクト**: rea-api
- **フレームワーク**: FastAPI

## 🎯 エンドポイントファイル
- **検出数**: {len(endpoint_files)}
- **ファイル一覧**:
"""
        
        for endpoint_file in endpoint_files:
            content += f"  - `{endpoint_file.name}`\n"
        
        content += """
## 🔌 主要エンドポイント
- `GET /api/v1/properties/` - 物件一覧取得
- `POST /api/v1/properties/` - 物件作成
- `GET /api/v1/properties/{id}` - 物件詳細取得
- `PUT /api/v1/properties/{id}` - 物件更新
- `DELETE /api/v1/properties/{id}` - 物件削除

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
"""
        
        # ファイル保存
        api_dir = self.get_output_dir("02_api")
        self.save_content(content, api_dir / "README.md")
        
        self.print_status("✅ API仕様生成完了")
        return {"api_path": str(api_path), "endpoint_files": len(endpoint_files)}