# generators/claude_memory_generator.py - 改訂版（シンプル・実用的）
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .base_generator import BaseGenerator


class ClaudeMemoryGenerator(BaseGenerator):
    """Claude記憶システム生成クラス"""

    def generate(self) -> Dict[str, Any]:
        """Claude用コンテキスト生成"""
        try:
            # プロジェクト状況を取得
            status = self._get_current_status()

            # コンテキスト生成
            content = self._generate_context(status)

            # ファイル保存（1ファイルのみ）
            memory_dir = self.output_dir / "claude_memory"
            memory_dir.mkdir(exist_ok=True)

            context_file = memory_dir / "CONTEXT.md"
            context_file.write_text(content, encoding="utf-8")

            self.print_status("✅ Claude記憶システム生成完了")
            return {
                "status": "success",
                "file": "claude_memory/CONTEXT.md",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.print_status(f"⚠️ Claude記憶システムエラー: {e}")
            return {"status": "error", "error": str(e)}

    def _get_current_status(self) -> Dict[str, Any]:
        """現在の状況を取得"""
        status = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "database": {"status": "unknown", "tables": 0},
            "files": {"total": 0},
            "errors": [],
        }

        try:
            # Pythonパス追加
            if str(self.base_path) not in sys.path:
                sys.path.insert(0, str(self.base_path))

            # DB状態確認
            try:
                from shared.database import READatabase

                if READatabase.test_connection():
                    tables = READatabase.get_all_tables()
                    status["database"] = {"status": "connected", "tables": len(tables)}
                else:
                    status["database"]["status"] = "disconnected"
                    status["errors"].append("DB接続失敗")
            except Exception as e:
                status["database"]["status"] = "error"
                status["errors"].append(f"DB接続エラー: {str(e)[:50]}")

            # ファイル数カウント
            file_count = 0
            for module_dir in self.base_path.iterdir():
                if module_dir.is_dir() and (
                    module_dir.name.startswith("rea-") or module_dir.name == "shared"
                ):
                    for py_file in module_dir.rglob("*.py"):
                        if "__pycache__" not in str(py_file):
                            file_count += 1
            status["files"]["total"] = file_count

        except Exception as e:
            status["errors"].append(f"状況取得エラー: {str(e)[:50]}")

        return status

    def _generate_context(self, status: Dict[str, Any]) -> str:
        """実用的なコンテキストを生成"""
        # DB状態
        db_status = status["database"]["status"]
        db_tables = status["database"].get("tables", 0)

        # エラー情報
        errors_section = ""
        if status["errors"]:
            errors_section = "\n## 現在のエラー\n"
            for error in status["errors"]:
                errors_section += f"- {error}\n"

        content = f"""# REAプロジェクトコンテキスト

更新日時: {status['timestamp']}
プロジェクトパス: /Users/yaguchimakoto/my_programing/REA

## 現在の状態

- データベース: {db_status} ({db_tables}テーブル)
- プログラムファイル: {status['files']['total']}ファイル
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
{errors_section}

## プロジェクト構造

- `rea-api/`: FastAPIバックエンド
- `rea-scraper/`: スクレイピングモジュール
- `shared/`: 共通ライブラリ
- `scripts/auto_spec_generator/`: 仕様書生成システム

## 共通ライブラリ

- `shared/database.py`: DB接続統一
- `shared/config.py`: 設定管理
- `shared/logger.py`: ログ管理
"""

        return content
