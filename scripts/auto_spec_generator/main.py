import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path
import sys
import os

# プロジェクトルートを動的に検出
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # scripts/auto_spec_generator -> REA

# Pythonパスに追加
sys.path.insert(0, str(PROJECT_ROOT))

from generators.api_generator import APIGenerator
from generators.claude_generator import ClaudeGenerator
from generators.claude_memory_generator import ClaudeMemoryGenerator
from generators.database_generator import DatabaseGenerator
from generators.navigation_generator import NavigationGenerator
from generators.program_structure_generator import ProgramStructureGenerator
from generators.scraper_generator import ScraperGenerator
from generators.shared_generator import SharedGenerator
from generators.shared_library_analyzer import SharedLibraryAnalyzer


class REASpecGeneratorController:
    """REA仕様書生成コントローラー（分割版）"""

    def __init__(self, base_path: str = None):
        # base_pathが指定されない場合は、動的に検出
        if base_path is None:
            self.base_path = PROJECT_ROOT
        else:
            self.base_path = Path(base_path)
        
        self.output_dir = self.base_path / "docs"
        
        # 環境情報を表示
        print(f"🔍 実行環境:")
        print(f"   プロジェクトルート: {self.base_path}")
        if os.environ.get('CODESPACES'):
            print(f"   環境: GitHub Codespaces ✅")
        else:
            print(f"   環境: ローカル")

    def generate_all(self):
        """全仕様書生成"""
        print("🚀 REA完全仕様書自動生成開始...")
        print(f"📁 プロジェクト: {self.base_path}")
        print(f"🕐 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # 生成クラス一覧
            generators = [
                ("📊 データベース仕様生成中...", DatabaseGenerator),
                ("🔌 API仕様生成中...", APIGenerator),
                ("🕷️ スクレイパー仕様生成中...", ScraperGenerator),
                ("📚 共通ライブラリ仕様生成中...", SharedGenerator),
                ("🔬 shared/ライブラリ完全分析中...", SharedLibraryAnalyzer),
                ("🏗️ プログラム構造仕様生成中...", ProgramStructureGenerator),
                ("🧠 Claude記憶システム生成中...", ClaudeMemoryGenerator),
                ("🧭 ナビゲーション生成中...", NavigationGenerator),
                ("🤖 Claude用チャンク生成中...", ClaudeGenerator),
            ]

            results = {}

            # 各生成クラスを実行
            for message, generator_class in generators:
                print(message)
                generator = generator_class(self.base_path, self.output_dir)
                result = generator.generate()
                results[generator_class.__name__] = result

            print("✅ 完全仕様書生成完了！")
            print(f"📁 出力先: {self.output_dir}")
            self._print_summary()

        except Exception as e:
            print(f"❌ エラー: {e}")
            print("🔧 データベース接続を確認してください")
            import traceback

            traceback.print_exc()

    def _print_summary(self):
        """生成結果サマリー表示"""
        print("\n📋 生成結果サマリー:")
        print("─────────────────────")

        # 生成されたファイルをカウント
        total_files = 0
        for md_file in self.output_dir.rglob("*.md"):
            total_files += 1

        print(f"📁 出力ディレクトリ: {self.output_dir}")
        print(f"📄 生成ファイル数: {total_files}")
        print("\n🗂️ 主要ファイル:")
        print("   📋 docs/README.md - メインナビゲーション")
        print("   📊 docs/01_database/current_structure.md - DB構造")
        print("   🔌 docs/02_api/README.md - API仕様")
        print("   🕷️ docs/03_scraper/README.md - スクレイパー仕様")
        print("   📚 docs/04_shared/README.md - 共通ライブラリ仕様")
        print("   🔬 docs/04_shared/complete_library_reference.md - shared/完全リファレンス")
        print("   🏗️ docs/05_program_structure/current_structure.md - プログラム構造")
        print("   🧠 docs/claude_memory/INSTANT_CONTEXT.md - Claude記憶システム")
        print("   🤖 docs/claude_chunks/ - Claude用最適化")

        print("\n🎯 次のアクション:")
        print("   1. docs/README.md を確認")
        print("   2. docs/04_shared/complete_library_reference.md でshared/完全把握")
        print("   3. docs/claude_memory/INSTANT_CONTEXT.md でClaude記憶喪失解決")
        print("   4. shared/database.py の活用でDB接続問題解決")
        print("   5. データベース分割計画を検討")
        print("   6. Claude連携テスト")

        print("\n🏆 分割リファクタリング完了:")
        print("   ✅ 700行 → 9ファイル×平均120行")
        print("   ✅ 単一責任原則適用")
        print("   ✅ 保守性・テスト性向上")
        print("   ✅ Claude記憶システム自動生成")
        print("   ✅ shared/ライブラリ完全分析システム")

    def display_file_content(self):
        """プログラム構造仕様の内容をターミナルに表示"""
        print("\n" + "=" * 80)
        print("📂 プログラム構造仕様書の内容")
        print("=" * 80 + "\n")

        # プログラム構造仕様ファイルのパス
        file_path = self.output_dir / "05_program_structure" / "current_structure.md"

        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(content)
                print("\n" + "=" * 80)
                print("✅ プログラム構造仕様書の表示完了")
                print("=" * 80)
            except Exception as e:
                print(f"❌ ファイルを読み込めませんでした: {e}")
        else:
            print(f"⚠️ ファイルが見つかりません: {file_path}")

    def display_summary_content(self):
        """主要ファイルの要約をターミナルに表示"""
        print("\n" + "=" * 80)
        print("📋 生成されたドキュメントの要約")
        print("=" * 80 + "\n")

        files_to_display = [
            ("データベース構造", "01_database/current_structure.md", 50),
            ("プログラム構造", "05_program_structure/current_structure.md", 50),
            ("共通ライブラリ", "04_shared/complete_library_reference.md", 30),
        ]

        for name, relative_path, lines in files_to_display:
            file_path = self.output_dir / relative_path
            if file_path.exists():
                print(f"\n### {name} ###")
                print(f"ファイル: {relative_path}")
                print("-" * 40)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content_lines = f.readlines()
                        # 最初のN行を表示
                        for i, line in enumerate(content_lines[:lines]):
                            print(line.rstrip())
                        if len(content_lines) > lines:
                            print(f"\n... (残り {len(content_lines) - lines} 行)")
                except Exception as e:
                    print(f"❌ 読み込みエラー: {e}")
            print("\n" + "=" * 80)


if __name__ == "__main__":
    # base_pathを指定せずに動的に検出
    controller = REASpecGeneratorController()

    # 仕様書を生成
    controller.generate_all()

    # プログラム構造仕様の内容をターミナルに表示
    controller.display_file_content()

    # または、主要ファイルの要約を表示
    # controller.display_summary_content()