"""
プロジェクト情報抽出モジュール
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import Config


class ProjectExtractor:
    def __init__(self):
        self.config = Config()

    def extract(self):
        """プロジェクト情報を抽出"""
        return {
            "overview": self._get_overview(),
            "structure": self._get_project_structure(),
            "implementation_status": self._get_implementation_status(),
        }

    def _get_overview(self):
        """プロジェクト概要"""
        return {
            "project_name": self.config.PROJECT_NAME,
            "description": self.config.DESCRIPTION,
            "project_path": str(self.config.PROJECT_ROOT),
            "current_phase": self.config.CURRENT_PHASE,
            "api_url": self.config.API_URL,
            "github": self.config.GITHUB,
        }

    def _get_project_structure(self):
        """プロジェクト構造を取得"""
        modules = [
            "rea-api",
            "rea-scraper",
            "rea-admin",
            "rea-search",
            "rea-publisher",
            "rea-wordpress",
        ]
        structure = {"modules": {}, "total_files": 0, "total_lines": 0}

        for module in modules:
            module_path = self.config.PROJECT_ROOT / module
            if module_path.exists():
                module_info = self._analyze_module(module_path)
                structure["modules"][module] = module_info
                structure["total_files"] += module_info["total_py_files"]
                structure["total_lines"] += module_info["total_lines"]

        return structure

    def _analyze_module(self, module_path):
        """モジュールの詳細分析"""
        info = {
            "exists": True,
            "status": self._get_module_status(module_path.name),
            "main_files": [],
            "config_files": [],
            "total_py_files": 0,
            "total_lines": 0,
            "directories": [],
        }

        # Pythonファイル数をカウント
        py_files = list(module_path.rglob("*.py"))
        info["total_py_files"] = len(
            [
                f
                for f in py_files
                if "venv" not in str(f) and "__pycache__" not in str(f)
            ]
        )

        # 主要ファイルの確認
        important_files = ["main.py", "app.py", "models.py", "schemas.py", "config.py"]
        for file in important_files:
            if (module_path / file).exists():
                info["main_files"].append(file)
            # appディレクトリ内も確認
            if (module_path / "app" / file).exists():
                info["main_files"].append(f"app/{file}")

        # 設定ファイルの確認
        config_files = [
            ".env",
            ".env.example",
            "requirements.txt",
            "package.json",
            "docker-compose.yml",
        ]
        for config in config_files:
            if (module_path / config).exists():
                info["config_files"].append(config)

        # 主要ディレクトリ
        for item in module_path.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and item.name not in ["venv", "__pycache__", "node_modules"]
            ):
                info["directories"].append(item.name)

        return info

    def _get_module_status(self, module_name):
        """モジュールの実装状態を返す"""
        status_map = {
            "rea-api": "✅ 完成・稼働中",
            "rea-scraper": "✅ Mac版実装完了",
            "rea-admin": "🔄 Phase 3実装予定",
            "rea-search": "⏳ Phase 5実装予定",
            "rea-publisher": "⏳ Phase 3実装予定",
            "rea-wordpress": "⏳ Phase 3実装予定",
        }
        return status_map.get(module_name, "❓ 未定")

    def _get_implementation_status(self):
        """実装状況"""
        return {
            "completed": self.config.COMPLETED_PHASES,
            "in_progress": self.config.IN_PROGRESS,
            "planned": self.config.PLANNED,
        }
