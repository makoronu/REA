# generators/database_generator.py - 改訂版（シンプル・実用的）
import sys
from pathlib import Path
from typing import Any, Dict

from .base_generator import BaseGenerator


class DatabaseGenerator(BaseGenerator):
    """データベース仕様生成クラス"""

    def generate(self) -> Dict[str, Any]:
        """データベース仕様生成"""
        try:
            # Pythonパスにベースパスを追加
            if str(self.base_path) not in sys.path:
                sys.path.insert(0, str(self.base_path))

            # 共通ライブラリを使用
            try:
                from shared.database import READatabase

                # DB接続テスト
                if not READatabase.test_connection():
                    return self._generate_fallback_spec("DB接続失敗")

                # DB健康チェック
                health = READatabase.health_check()

            except Exception as db_error:
                self.print_status(f"⚠️ DB接続エラー: {db_error}")
                return self._generate_fallback_spec(str(db_error))

            # テーブル一覧取得
            tables = READatabase.get_all_tables()
            total_columns = 0

            content = f"""# REAデータベース構造

生成日時: {self.get_timestamp()}
データベース: {health['database']}
テーブル数: {len(tables)}

## テーブル一覧

| テーブル名 | カラム数 | レコード数 | 用途 |
|------------|----------|------------|------|
"""

            # テーブル情報を取得
            for table in sorted(tables):
                try:
                    table_info = READatabase.get_table_info(table)
                    column_count = table_info["column_count"]
                    record_count = table_info["record_count"]
                    total_columns += column_count
                    purpose = self._get_table_purpose(table)
                    content += (
                        f"| {table} | {column_count} | {record_count:,} | {purpose} |\n"
                    )
                except Exception as e:
                    content += f"| {table} | - | - | エラー |\n"

            content += f"\n総カラム数: {total_columns}\n"

            # 各テーブルの詳細
            content += "\n## テーブル詳細\n"

            for table in sorted(tables):
                try:
                    table_info = READatabase.get_table_info(table)
                    columns = table_info["columns"]

                    content += f"\n### {table}\n"
                    content += f"- カラム数: {table_info['column_count']}\n"
                    content += f"- レコード数: {table_info['record_count']:,}\n"

                    if columns:
                        content += "\n| カラム名 | データ型 |\n"
                        content += "|----------|----------|\n"
                        for col in columns[:10]:  # 最初の10カラムのみ
                            content += (
                                f"| {col['column_name']} | {col['data_type']} |\n"
                            )
                        if len(columns) > 10:
                            content += f"\n他 {len(columns)-10} カラム\n"

                except Exception:
                    content += f"\n### {table}\n取得エラー\n"

            # ファイル保存
            db_dir = self.get_output_dir("01_database")
            self.save_content(content, db_dir / "current_structure.md")

            self.print_status(f"✅ データベース仕様生成完了: {len(tables)}テーブル")
            return {"success": True, "tables": tables, "total_columns": total_columns}

        except Exception as e:
            self.print_status(f"❌ データベース分析エラー: {e}")
            return self._generate_fallback_spec(str(e))

    def _generate_fallback_spec(self, error_message: str) -> Dict[str, Any]:
        """DB接続失敗時のフォールバック仕様書生成"""
        fallback_content = f"""# データベース接続エラー

エラー: {error_message}
発生時刻: {self.get_timestamp()}

## 対処方法

1. Docker PostgreSQL起動
   ```
   docker-compose up -d
   ```

2. 接続テスト
   プロジェクトルートで実行:
   ```
   python -c "from shared.database import READatabase; print(READatabase.test_connection())"
   ```

3. 環境変数確認
   ```
   echo $DATABASE_URL
   ```
"""

        # フォールバック仕様書を保存
        db_dir = self.get_output_dir("01_database")
        self.save_content(fallback_content, db_dir / "current_structure.md")

        return {"success": False, "error": error_message}

    def _get_table_purpose(self, table_name: str) -> str:
        """テーブル用途を推定"""
        # 既知のテーブル
        known_tables = {
            "properties": "物件情報",
            "equipment_master": "設備マスター",
            "property_equipment": "物件-設備関連",
            "building_structure": "建物構造",
            "current_status": "現況",
            "property_types": "物件種別",
            "zoning_districts": "用途地域",
            "land_rights": "土地権利",
            "floor_plan_room_types": "間取りタイプ",
            "image_types": "画像種別",
            "column_labels": "カラムメタデータ",
        }

        if table_name in known_tables:
            return known_tables[table_name]

        # パターンマッチング
        if "_master" in table_name:
            return "マスターデータ"
        elif "properties_" in table_name:
            return "物件関連"
        elif "_log" in table_name:
            return "ログ"

        return "不明"
