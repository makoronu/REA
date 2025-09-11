# generators/claude_generator.py
from pathlib import Path
from typing import Any, Dict

from .base_generator import BaseGenerator


class ClaudeGenerator(BaseGenerator):
    """Claude用チャンク生成クラス"""

    def generate(self) -> Dict[str, Any]:
        """Claude用チャンク生成"""
        chunks_dir = self.get_output_dir("claude_chunks")

        # データベースチャンク
        self._generate_database_chunk(chunks_dir)

        # APIチャンク
        self._generate_api_chunk(chunks_dir)

        # 共通ライブラリチャンク
        self._generate_shared_chunk(chunks_dir)

        self.print_status("✅ Claude用チャンク生成完了")
        return {"chunks": "completed"}

    def _generate_database_chunk(self, chunks_dir: Path) -> None:
        """データベースチャンク生成"""
        db_chunks_dir = chunks_dir / "database_chunks"
        db_chunks_dir.mkdir(exist_ok=True)

        db_chunk_content = f"""# 🤖 Claude専用：REAデータベース情報

> **最適化済みチャンク** - Claude用に情報を最適化

## 📊 重要な事実
- **メインテーブル**: properties（294カラム）
- **分割必要**: 機能別8テーブルに分割推奨
- **マスターテーブル**: 10個（equipment_master等）
- **データベース名**: real_estate_db
- **接続方式**: shared/database.py 統一システム

## 🎯 properties テーブル問題
- **294カラム**: 管理困難・パフォーマンス問題
- **推奨分割**:
  - properties_core（基本情報）
  - properties_images（画像30枚分）
  - properties_pricing（価格・収益）
  - properties_location（住所・交通）
  - properties_building（建物情報）
  - properties_contract（契約情報）
  - properties_land（土地情報）  
  - properties_facilities（周辺施設）

## 🔧 DB接続の統一化（重要）
- **従来**: 各モジュールで個別接続
- **新方式**: `shared/database.py` で統一
- **利点**: エラー激減、保守性向上、コード重複排除

## 💡 よくある質問への回答
**Q: テーブル分割は必要？**
A: 絶対必要。294カラムは非現実的。

**Q: どの順序で分割する？**
A: 1)画像 2)価格 3)住所 4)建物...の順

**Q: データは失われる？**
A: いいえ。分割はデータ移行で安全に実行。

**Q: DB接続エラーが頻発するのは？**
A: shared/database.py を使えば解決。統一された接続システム。
"""

        self.save_content(db_chunk_content, db_chunks_dir / "overview.md")

    def _generate_api_chunk(self, chunks_dir: Path) -> None:
        """APIチャンク生成"""
        api_chunks_dir = chunks_dir / "api_chunks"
        api_chunks_dir.mkdir(exist_ok=True)

        api_chunk_content = f"""# 🤖 Claude専用：REA API情報

## 🔌 重要な事実
- **URL**: http://localhost:8005
- **フレームワーク**: FastAPI
- **ドキュメント**: http://localhost:8005/docs
- **起動**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8005`

## 📋 主要エンドポイント
- `GET /api/v1/properties/` - 物件一覧
- `POST /api/v1/properties/` - 物件作成
- `GET /api/v1/properties/{{id}}` - 物件詳細

## 🔧 DB接続統一化対応
- **推奨**: shared/database.py 使用
- **利点**: 接続エラー撲滅、統一性確保

## 💡 開発時の注意
- ポート8005で起動
- Swagger UIで動作確認
- PostgreSQL接続必須
- 環境変数設定: `export DATABASE_URL="postgresql://rea_user:rea_password@localhost/real_estate_db"`
"""

        self.save_content(api_chunk_content, api_chunks_dir / "overview.md")

    def _generate_shared_chunk(self, chunks_dir: Path) -> None:
        """共通ライブラリチャンク生成"""
        shared_chunks_dir = chunks_dir / "shared_chunks"
        shared_chunks_dir.mkdir(exist_ok=True)

        shared_chunk_content = f"""# 🤖 Claude専用：REA共通ライブラリ情報

## 📚 実装済みライブラリ

### database.py（重要）
**目的**: DB接続問題の根本解決
**機能**:
- `READatabase.get_connection()` - 統一接続
- `READatabase.health_check()` - 健康状態確認
- `READatabase.get_all_tables()` - テーブル一覧
- `READatabase.test_connection()` - 接続テスト

**使用例**:
```python
from shared.database import READatabase

# 接続テスト
if READatabase.test_connection():
    print("✅ 接続成功")

# テーブル一覧
tables = READatabase.get_all_tables()
```

## 💡 重要な事実
- **問題**: 毎回DB接続でつまづく
- **解決**: shared/database.py で統一
- **効果**: エラー激減、開発効率向上

## 🔧 環境変数設定（忘れやすい）
```bash
export DATABASE_URL="postgresql://rea_user:rea_password@localhost/real_estate_db"
```

**これを忘れると接続失敗する！**
"""

        self.save_content(shared_chunk_content, shared_chunks_dir / "overview.md")
