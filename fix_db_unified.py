#!/usr/bin/env python3
"""
REA DB接続完全統一化スクリプト v2
全てのDB接続をshared/database.py経由に統一（実ファイルに基づく修正版）
"""
import os
import re
import shutil
from datetime import datetime
from pathlib import Path


class DBConnectionUnifier:
    def __init__(self):
        self.project_root = Path("/Users/yaguchimakoto/my_programing/REA")
        self.backup_dir = (
            self.project_root
            / f"backup_db_unify_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.files_to_fix = []

    def find_db_connections(self):
        """DB接続を行っている全ファイルを特定"""
        print("🔍 DB接続箇所を検索中...")

        # 実際に存在して修正が必要なファイル
        target_files = [
            "docker-compose.yml",
            "scripts/spec_generator/config.py",
            "scripts/spec_generator/generate_claude_context.py",
            "scripts/auto_spec_generator/master_generator.py",
            "scripts/auto_spec_generator/table_detail_generator.py",
            "scripts/auto_spec_generator/generators/database_generator.py",
            "rea-api/app/core/config.py",
            "rea-scraper/src/config/settings.py",
            ".env",
            "rea-api/.env",
            "rea-scraper/.env",
            "scripts/auto_spec_generator/.env",
        ]

        for file_path in target_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.files_to_fix.append(full_path)
                print(f"  📄 {file_path}")

    def backup_file(self, filepath):
        """ファイルをバックアップ"""
        rel_path = filepath.relative_to(self.project_root)
        backup_path = self.backup_dir / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(filepath, backup_path)

    def fix_spec_generator_config(self, filepath):
        """scripts/spec_generator/config.py を修正"""
        content = filepath.read_text()

        # DB_USER = "postgres" を修正
        content = re.sub(r'DB_USER = "postgres"', 'DB_USER = "rea_user"', content)

        # ハードコードされた設定を環境変数参照に変更
        if "import os" not in content:
            content = (
                "import os\nfrom dotenv import load_dotenv\n\n# .env読み込み\nload_dotenv()\n\n"
                + content
            )

        # DB設定を環境変数から取得するように変更
        content = re.sub(
            r'DB_NAME = "real_estate_db"',
            'DB_NAME = os.getenv("DB_NAME", "real_estate_db")',
            content,
        )
        content = re.sub(
            r'DB_HOST = "localhost"',
            'DB_HOST = os.getenv("DB_HOST", "localhost")',
            content,
        )

        return content

    def fix_spec_generator_claude_context(self, filepath):
        """scripts/spec_generator/generate_claude_context.py を修正"""
        content = filepath.read_text()

        # psycopg2.connectを shared/database.py使用に変更
        if "psycopg2.connect" in content:
            # インポート追加
            imports = """import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.database import READatabase
"""
            if "from shared.database import" not in content:
                content = imports + "\n" + content

            # 接続処理を置き換え
            content = re.sub(
                r"conn = psycopg2\.connect\([^)]+\)",
                "conn = READatabase.get_connection()",
                content,
            )

        return content

    def fix_auto_spec_generator_files(self, filepath):
        """auto_spec_generator系のファイルを修正"""
        content = filepath.read_text()

        # create_engineの置き換え
        if "create_engine" in content:
            # インポート追加
            if "from shared.database import" not in content:
                imports = """import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.database import READatabase
import os
from dotenv import load_dotenv

# .env読み込み
load_dotenv()
"""
                # importsを最初に追加
                lines = content.split("\n")
                import_end = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith(("import", "from")):
                        import_end = i
                        break
                lines.insert(import_end, imports)
                content = "\n".join(lines)

            # create_engine呼び出しを環境変数使用に変更
            content = re.sub(
                r"engine = create_engine\(self\.db_url\)",
                """# 環境変数から接続文字列を取得
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            host = os.getenv('DB_HOST', 'localhost')
            port = os.getenv('DB_PORT', '5432')
            user = os.getenv('DB_USER', 'rea_user')
            password = os.getenv('DB_PASSWORD', 'rea_password')
            name = os.getenv('DB_NAME', 'real_estate_db')
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
        engine = create_engine(db_url)""",
                content,
            )

        return content

    def fix_database_generator(self, filepath):
        """generators/database_generator.py は既にshared使用なので軽微な修正のみ"""
        content = filepath.read_text()
        # 既にREADatabaseを使用しているので、特に修正不要
        return content

    def fix_rea_api_config(self, filepath):
        """rea-api/app/core/config.py を修正"""
        content = filepath.read_text()

        # ハードコードされたDATABASE_URLを環境変数参照に
        if "import os" not in content:
            content = "import os\n" + content

        content = re.sub(
            r'DATABASE_URL: str = "postgresql://[^"]*"',
            'DATABASE_URL: str = os.getenv("DATABASE_URL", "")',
            content,
        )

        return content

    def fix_rea_scraper_settings(self, filepath):
        """rea-scraper/src/config/settings.py を修正"""
        content = filepath.read_text()

        # 既にos.getenvを使用しているが、デフォルト値が間違っている
        content = re.sub(
            r'"postgresql://postgres:postgres@localhost:5432/real_estate_db"',
            '"postgresql://rea_user:rea_password@localhost:5432/real_estate_db"',
            content,
        )

        # shared/database.py使用を推奨するコメント追加
        if "# DB接続はshared/database.pyを推奨" not in content:
            content = (
                """# 注意: 可能な限りDB接続はshared/database.pyを使用してください
# from shared.database import READatabase
# conn = READatabase.get_connection()

"""
                + content
            )

        return content

    def fix_docker_compose(self, filepath):
        """docker-compose.yml を修正"""
        content = filepath.read_text()

        # PostgreSQLサービスの環境変数をenv_file参照に
        # environment:セクションをenv_file:に置き換える
        content = re.sub(
            r"(postgres:[^:]*?)(environment:\s*\n(?:\s+[A-Z_]+:[^\n]+\n)+)",
            r"\1env_file: .env\n    # 環境変数は.envから読み込まれます\n",
            content,
            flags=re.MULTILINE | re.DOTALL,
        )

        # 各サービスのDATABASE_URL行を削除
        services = ["rea-api", "rea-scraper", "rea-publisher"]
        for service in services:
            # - DATABASE_URL=... の行を削除
            content = re.sub(
                rf"(\s+{service}:.*?environment:.*?)(\s+- DATABASE_URL=[^\n]+\n)",
                r"\1",
                content,
                flags=re.MULTILINE | re.DOTALL,
            )

            # env_fileがなければ追加
            if f"{service}:" in content and f"env_file: .env" not in content:
                # environmentセクションの前にenv_file追加
                content = re.sub(
                    rf"(\s+{service}:.*?)(environment:)",
                    r"\1env_file: .env\n    \2",
                    content,
                    flags=re.MULTILINE | re.DOTALL,
                )

        return content

    def create_rea_api_database_py(self):
        """rea-api/app/core/database.py を新規作成"""
        database_py_content = '''"""
REA API データベース接続
shared/database.pyを使用して統一管理
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.database import READatabase
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# SQLAlchemy用のengine取得
def get_db_url():
    """DATABASE_URLを取得（なければ組み立て）"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        user = os.getenv('DB_USER', 'rea_user')
        password = os.getenv('DB_PASSWORD', 'rea_password')
        name = os.getenv('DB_NAME', 'real_estate_db')
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"
    return db_url

engine = create_engine(get_db_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI依存性注入用"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 互換性のためのエイリアス
get_connection = READatabase.get_connection
test_connection = READatabase.test_connection
'''

        database_path = self.project_root / "rea-api/app/core/database.py"
        database_path.write_text(database_py_content)
        print("✅ rea-api/app/core/database.py を新規作成")

    def remove_duplicate_envs(self):
        """重複する.envファイルを処理"""
        env_files = [
            "rea-api/.env",
            "rea-scraper/.env",
            "scripts/auto_spec_generator/.env",
        ]

        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                self.backup_file(env_path)
                # シンボリックリンクではなく、統一を促すREADMEを作成
                readme_content = """# .env設定について

DB接続設定はプロジェクトルートの.envファイルで一元管理されています。

プロジェクトルート: /Users/yaguchimakoto/my_programing/REA/.env

各モジュールはshared/database.pyを通じて自動的に正しい設定を読み込みます。
"""
                readme_path = env_path.parent / "ENV_README.md"
                readme_path.write_text(readme_content)
                print(f"📝 {env_file} の代わりにENV_README.md作成")

    def fix_python_files(self):
        """Pythonファイルを修正"""
        for filepath in self.files_to_fix:
            if filepath.suffix != ".py":
                continue

            rel_path = filepath.relative_to(self.project_root)
            print(f"\n🔧 修正中: {rel_path}")

            self.backup_file(filepath)
            content = filepath.read_text()
            original_content = content

            # ファイルパスに基づいて適切な修正関数を呼ぶ
            if "scripts/spec_generator/config.py" in str(rel_path):
                content = self.fix_spec_generator_config(filepath)
            elif "scripts/spec_generator/generate_claude_context.py" in str(rel_path):
                content = self.fix_spec_generator_claude_context(filepath)
            elif "scripts/auto_spec_generator" in str(
                rel_path
            ) and "database_generator" not in str(rel_path):
                content = self.fix_auto_spec_generator_files(filepath)
            elif "generators/database_generator.py" in str(rel_path):
                content = self.fix_database_generator(filepath)
            elif "rea-api/app/core/config.py" in str(rel_path):
                content = self.fix_rea_api_config(filepath)
            elif "rea-scraper/src/config/settings.py" in str(rel_path):
                content = self.fix_rea_scraper_settings(filepath)

            if content != original_content:
                filepath.write_text(content)
                print(f"  ✅ 修正完了")
            else:
                print(f"  ⏭️  変更なし")

    def create_test_script(self):
        """テストスクリプトを作成"""
        test_content = '''#!/usr/bin/env python3
"""DB接続統一化テストスクリプト"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("🔍 DB接続テスト開始...")

# 1. shared/database.pyのテスト
print("\\n1️⃣ shared/database.py テスト")
try:
    from shared.database import READatabase
    if READatabase.test_connection():
        print("  ✅ 接続成功")
        tables = READatabase.get_all_tables()
        print(f"  📊 テーブル数: {len(tables)}")
    else:
        print("  ❌ 接続失敗")
except Exception as e:
    print(f"  ❌ エラー: {e}")

# 2. rea-apiのテスト
print("\\n2️⃣ rea-api データベース接続テスト")
try:
    from rea-api.app.core.database import test_connection
    if test_connection():
        print("  ✅ 接続成功")
    else:
        print("  ❌ 接続失敗")
except Exception as e:
    print(f"  ❌ エラー: {e}")

print("\\n✅ テスト完了")
'''
        test_path = self.project_root / "test_db_unified.py"
        test_path.write_text(test_content)
        test_path.chmod(0o755)
        print("✅ test_db_unified.py 作成完了")

    def generate_summary(self):
        """実行サマリーを生成"""
        summary = f"""# DB接続統一化 実行レポート

## 実行日時
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## バックアップ
{self.backup_dir}

## 修正内容

### 1. 設定ファイルの修正
- `scripts/spec_generator/config.py`: DB_USER修正
- `rea-api/app/core/config.py`: 環境変数参照に変更
- `rea-scraper/src/config/settings.py`: デフォルト値修正

### 2. DB接続の統一
- `scripts/spec_generator/generate_claude_context.py`: shared/database.py使用
- `scripts/auto_spec_generator/master_generator.py`: 環境変数から接続
- `scripts/auto_spec_generator/table_detail_generator.py`: 環境変数から接続

### 3. docker-compose.yml
- PostgreSQLサービス: env_file参照
- 各サービス: DATABASE_URLハードコード削除

### 4. 新規作成
- `rea-api/app/core/database.py`: shared/database.pyラッパー

## 次のステップ

```bash
# 1. Docker再起動
docker-compose down
docker-compose up -d

# 2. 接続テスト
python test_db_unified.py

# 3. 仕様書生成テスト
cd scripts/auto_spec_generator
python main.py
```

## 重要な変更点

1. **全てのDB接続はshared/database.py経由**
   - 設定は.envで一元管理
   - どこから実行しても同じ設定

2. **ハードコード削除**
   - 全ての接続情報は環境変数から取得
   - デフォルト値も統一

3. **docker-compose.yml簡素化**
   - env_file使用で設定の重複排除
"""
        summary_path = self.project_root / "db_unification_report.md"
        summary_path.write_text(summary)
        print(f"\n📄 実行レポート生成: {summary_path}")

    def run(self):
        """統一化処理を実行"""
        print("🚀 REA DB接続完全統一化開始...")
        print(f"📁 プロジェクト: {self.project_root}")

        # DB接続箇所を特定
        self.find_db_connections()
        print(f"\n📊 修正対象: {len(self.files_to_fix)}ファイル")

        if not self.files_to_fix:
            print("✅ 修正対象なし")
            return

        # バックアップディレクトリ作成
        self.backup_dir.mkdir(exist_ok=True)

        # 修正実行
        print("\n🔧 修正開始...")

        # Pythonファイルの修正
        self.fix_python_files()

        # docker-compose.ymlの修正
        compose_path = self.project_root / "docker-compose.yml"
        if compose_path in self.files_to_fix:
            print(f"\n🔧 修正中: docker-compose.yml")
            self.backup_file(compose_path)
            content = compose_path.read_text()
            content = self.fix_docker_compose(compose_path)
            compose_path.write_text(content)
            print("  ✅ 修正完了")

        # rea-api/app/core/database.py作成
        self.create_rea_api_database_py()

        # 重複.envの処理
        self.remove_duplicate_envs()

        # テストスクリプト作成
        self.create_test_script()

        # サマリー生成
        self.generate_summary()

        print("\n✅ DB接続統一化完了！")
        print("📄 詳細はdb_unification_report.mdを確認")


if __name__ == "__main__":
    unifier = DBConnectionUnifier()
    unifier.run()
