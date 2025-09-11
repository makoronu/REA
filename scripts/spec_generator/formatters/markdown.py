"""
Markdown形式フォーマッター
"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import Config


class MarkdownFormatter:
    def __init__(self):
        self.config = Config()
        self.lines = []

    def format(self, spec_data):
        """仕様データをMarkdown形式に変換"""
        self.lines = []

        # ヘッダー
        self._add_header(spec_data)

        # 各セクション
        self._add_overview(spec_data.get("project", {}).get("overview", {}))
        self._add_project_structure(spec_data.get("project", {}).get("structure", {}))
        self._add_database(spec_data.get("database", {}))
        self._add_api(spec_data.get("api", {}))
        self._add_implementation_status(
            spec_data.get("project", {}).get("implementation_status", {})
        )
        self._add_recent_changes(spec_data.get("git", {}))
        self._add_development_guide()

        return "\n".join(self.lines)

    def _add_header(self, spec_data):
        """ヘッダー部分"""
        self.lines.append("# 🏢 REA Project Complete Specification")
        self.lines.append(f"\n**Generated**: {spec_data.get('generated_at', '')}")
        self.lines.append(f"**Mode**: {spec_data.get('mode', '')}")
        self.lines.append("\n---\n")

    def _add_overview(self, overview):
        """概要セクション"""
        self.lines.append("## 🚀 Overview")
        for key, value in overview.items():
            label = key.replace("_", " ").title()
            self.lines.append(f"- **{label}**: {value}")

    def _add_project_structure(self, structure):
        """プロジェクト構造セクション"""
        if not structure or not structure.get("modules"):
            return

        self.lines.append("\n## 📁 Project Structure")
        self.lines.append(f"\n**Total Files**: {structure.get('total_files', 0)}")
        self.lines.append(f"**Total Lines**: {structure.get('total_lines', 0):,}")

        for module_name, info in structure.get("modules", {}).items():
            self.lines.append(f"\n### {module_name} {info.get('status', '')}")

            if info.get("exists"):
                self.lines.append(f"- Python Files: {info.get('total_py_files', 0)}")
                self.lines.append(
                    f"- Directories: {', '.join(info.get('directories', []))}"
                )

                if info.get("main_files"):
                    self.lines.append("\n**Main Files:**")
                    for file in info["main_files"][:5]:
                        self.lines.append(f"- {file}")

                if info.get("config_files"):
                    self.lines.append("\n**Config Files:**")
                    for file in info["config_files"]:
                        self.lines.append(f"- {file}")

    def _add_database(self, db_data):
        """データベースセクション"""
        self.lines.append("\n## 📊 Database Structure")

        # サマリー
        summary = db_data.get("summary", {})
        if summary:
            self.lines.append("\n### Summary")
            for key, value in summary.items():
                label = key.replace("_", " ").title()
                self.lines.append(f"- **{label}**: {value:,}")

        # ENUM型
        if db_data.get("enums"):
            self._add_enums(db_data["enums"])

        # テーブル詳細
        if db_data.get("tables"):
            self._add_tables(db_data["tables"])

    def _add_enums(self, enums):
        """ENUM型定義"""
        self.lines.append("\n### ENUM Type Definitions")
        self.lines.append("| ENUM Name | Values |")
        self.lines.append("|-----------|--------|")

        for enum_name, values in enums.items():
            values_str = ", ".join(values[:5])
            if len(values) > 5:
                values_str += f" ... ({len(values)} total)"
            self.lines.append(f"| {enum_name} | {values_str} |")

    def _add_tables(self, tables):
        """テーブル情報"""
        self.lines.append("\n### Table Details")

        for table_name, info in tables.items():
            self.lines.append(f"\n#### {table_name}")
            self.lines.append(f"- Columns: {info['columns']}")
            self.lines.append(f"- Records: {info['records']:,}")

            # propertiesテーブルは特別扱い
            if table_name == "properties" and "column_groups" in info:
                self._add_properties_columns(info["column_groups"])
            elif info.get("column_details"):
                self._add_column_details(info["column_details"])

    def _add_properties_columns(self, column_groups):
        """propertiesテーブルのカラム情報"""
        for group_name, columns in column_groups.items():
            self.lines.append(f"\n**{group_name} ({len(columns)}カラム):**")
            self.lines.append("| Column | Type | Nullable | Japanese Label |")
            self.lines.append("|--------|------|----------|----------------|")

            for col in columns[:10]:
                self.lines.append(
                    f"| {col['name']} | {col['type']} | {col['nullable']} | {col['japanese_label']} |"
                )

            if len(columns) > 10:
                self.lines.append(
                    f"| ... | ({len(columns) - 10} more columns) | ... | ... |"
                )

    def _add_column_details(self, columns):
        """通常テーブルのカラム情報"""
        self.lines.append("\n**主要カラム:**")
        self.lines.append("| Column | Type | Nullable | Japanese Label |")
        self.lines.append("|--------|------|----------|----------------|")

        for col in columns:
            self.lines.append(
                f"| {col['name']} | {col['type']} | {col['nullable']} | {col['japanese_label']} |"
            )

    def _add_api(self, api_data):
        """APIセクション"""
        self.lines.append("\n## 🔌 API Specification")

        total = api_data.get("total_endpoints", 0)
        self.lines.append(f"\n### Total Endpoints: {total}")
        self.lines.append(f"**Base URL**: {api_data.get('base_url', '')}\n")

        endpoints = api_data.get("endpoints", [])
        if endpoints:
            self.lines.append("| Method | Path | Summary |")
            self.lines.append("|--------|------|---------|")
            for ep in endpoints:
                self.lines.append(
                    f"| {ep['method']} | {ep['path']} | {ep['summary']} |"
                )

    def _add_implementation_status(self, impl_data):
        """実装状況セクション"""
        self.lines.append("\n## 💻 Implementation Status")

        # 完了
        if impl_data.get("completed"):
            self.lines.append("\n### ✅ Completed")
            for phase in impl_data["completed"]:
                self.lines.append(f"\n**{phase['phase']}: {phase['name']}**")
                for detail in phase.get("details", []):
                    self.lines.append(f"- {detail}")

        # 進行中
        if impl_data.get("in_progress"):
            prog = impl_data["in_progress"]
            self.lines.append(f"\n### 🔄 In Progress")
            self.lines.append(
                f"**{prog['phase']}: {prog['name']}** ({prog['progress']})"
            )

        # 予定
        if impl_data.get("planned"):
            self.lines.append("\n### ⏳ Planned")
            for plan in impl_data["planned"]:
                self.lines.append(f"- {plan}")

    def _add_recent_changes(self, git_data):
        """最近の変更セクション"""
        self.lines.append("\n## 📝 Recent Changes")

        self.lines.append(f"\n**Last Update**: {git_data.get('last_update', '')}")
        self.lines.append(f"**Current Branch**: {git_data.get('branch', 'main')}")

        commits = git_data.get("recent_commits", [])
        if commits:
            self.lines.append("\n**Recent Commits:**")
            for commit in commits[:5]:
                self.lines.append(f"- {commit}")

        stats = git_data.get("stats", {})
        if stats.get("total_commits"):
            self.lines.append(f"\n**Total Commits**: {stats['total_commits']}")

    def _add_development_guide(self):
        """開発ガイドセクション"""
        self.lines.append("\n## 🛠 Development Guide")

        # Tech Stack
        self.lines.append("\n### Tech Stack")
        for category, techs in self.config.TECH_STACK.items():
            self.lines.append(f"\n**{category.title()}:**")
            for tech in techs:
                self.lines.append(f"- {tech}")

        # Code Patterns
        self.lines.append("\n### Code Patterns")
        self.lines.append("- **Api**: FastAPI + Pydantic + SQLAlchemy")
        self.lines.append("- **Scraping**: 段階処理 + Bot対策")
        self.lines.append("- **Error Handling**: 全体書き直し方式")

        # Important Notes
        self.lines.append("\n### Important Notes")
        self.lines.append("- Mac環境（macOS）で開発")
        self.lines.append(f"- プロジェクトパス: {self.config.PROJECT_ROOT}")
        self.lines.append("- Python仮想環境: ./venv")
        self.lines.append("- ポート: API=8005, DB=5432")
