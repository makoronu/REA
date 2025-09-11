# generators/database_generator.py - DB接続エラー修正版
import sys
from pathlib import Path
from typing import Any, Dict

from .base_generator import BaseGenerator


class DatabaseGenerator(BaseGenerator):
    """データベース仕様生成クラス（接続エラー対応版）"""

    def generate(self) -> Dict[str, Any]:
        """データベース仕様生成"""
        try:
            # Pythonパスにベースパスを追加
            sys.path.append(str(self.base_path))

            # 統一DB接続システムを使用（エラー対応版）
            try:
                from shared.database import READatabase

                # DB健康チェック（エラー時はフォールバック）
                health = READatabase.health_check()
                if health["status"] != "healthy":
                    self.print_status(
                        f"⚠️ DB接続警告: {health.get('error', 'Unknown error')}"
                    )
                    return self._generate_fallback_spec("DB接続失敗")

            except Exception as db_error:
                self.print_status(f"⚠️ DB接続エラー: {db_error}")
                return self._generate_fallback_spec(str(db_error))

            # テーブル一覧取得
            tables = READatabase.get_all_tables()
            total_columns = 0

            content = f"""# 📊 REAデータベース現在構造

## 📋 生成情報
- **生成日時**: {self.get_timestamp()}
- **データベース**: {health['database']}
- **テーブル数**: {len(tables)}
- **接続方式**: {health['config_source']}
- **応答時間**: {health['response_time_ms']}ms

## 📈 テーブル一覧

| No | テーブル名 | カラム数 | レコード数 | 用途 |
|----|------------|----------|------------|------|
"""

            for i, table in enumerate(tables, 1):
                try:
                    # 統一DB接続でテーブル情報取得
                    table_info = READatabase.get_table_info(table)
                    column_count = table_info["column_count"]
                    record_count = table_info["record_count"]
                    total_columns += column_count
                    # 🚀 新テーブル自動検出機能を使用
                    purpose = self._get_table_purpose_auto(table)
                    content += f"| {i} | `{table}` | {column_count} | {record_count} | {purpose} |\n"
                except Exception as table_error:
                    self.print_status(f"⚠️ テーブル {table} 分析エラー: {table_error}")
                    content += f"| {i} | `{table}` | - | - | 分析エラー |\n"

            content += f"""
## 📊 統計サマリー
- **総テーブル数**: {len(tables)}
- **総カラム数**: {total_columns}
- **接続状態**: ✅ 健全 ({health['response_time_ms']}ms)
- **PostgreSQL版**: {health.get('version', 'Unknown')[:50]}...
- **最大テーブル**: properties ({READatabase.get_table_info('properties')['column_count'] if 'properties' in tables else 0}カラム)

## 🎯 重要テーブル詳細

### properties テーブル
"""

            if "properties" in tables:
                try:
                    props_info = READatabase.get_table_info("properties")
                    content += f"- **カラム数**: {props_info['column_count']}\n"
                    content += f"- **レコード数**: {props_info['record_count']}\n"
                    content += f"- **分割推奨**: 機能別に8テーブルに分割推奨\n"
                    content += f"- **主要カラム**: id, title, price, address_name\n"
                except Exception:
                    content += "- **状態**: 分析エラー\n"

            # テーブル詳細
            content += "\n## 📋 全テーブル詳細\n"

            for table in tables:
                try:
                    table_info = READatabase.get_table_info(table)
                    columns = table_info["columns"]
                    column_count = table_info["column_count"]
                    record_count = table_info["record_count"]

                    content += f"\n### {table}\n"
                    content += f"**カラム数**: {column_count}  \n"
                    content += f"**レコード数**: {record_count}  \n"
                    content += f"**推定用途**: {self._get_table_purpose_auto(table)}  \n"

                    # 詳細洞察を追加
                    insights = self._get_table_insights(table)
                    if insights:
                        content += f"**詳細**: {insights}  \n"

                    # 主要カラムを表示（最初の5つ）
                    if columns:
                        content += "**主要カラム**: "
                        main_columns = [col["column_name"] for col in columns[:5]]
                        content += ", ".join(main_columns)
                        if len(columns) > 5:
                            content += f" ...他{len(columns)-5}カラム"
                        content += "\n"

                    # データ型情報
                    if columns:
                        content += "**データ型例**: "
                        type_examples = []
                        for col in columns[:3]:
                            col_name = col["column_name"]
                            col_type = col["data_type"]
                            type_examples.append(f"{col_name}({col_type})")
                        content += ", ".join(type_examples)
                        if len(columns) > 3:
                            content += "..."
                        content += "\n"

                except Exception as detail_error:
                    content += f"\n### {table}\n"
                    content += f"**状態**: 詳細分析エラー - {detail_error}\n"

            # ファイル保存
            db_dir = self.get_output_dir("01_database")
            self.save_content(content, db_dir / "current_structure.md")

            self.print_status(f"✅ データベース構造: {len(tables)}テーブル分析完了")
            return {
                "success": True,
                "tables": tables,
                "total_columns": total_columns,
                "connection_info": health,
            }

        except Exception as e:
            self.print_status(f"❌ データベース分析エラー: {e}")
            return self._generate_fallback_spec(str(e))

    def _generate_fallback_spec(self, error_message: str) -> Dict[str, Any]:
        """DB接続失敗時のフォールバック仕様書生成"""
        fallback_content = f"""# ❌ データベース接続エラー

## 🚨 エラー内容
```
{error_message}
```

## 🔧 対処方法

### 1. Docker PostgreSQL起動確認
```bash
docker ps | grep postgres
docker-compose up -d
```

### 2. 環境変数設定
```bash
export DATABASE_URL="postgresql://rea_user:rea_password@localhost/real_estate_db"
```

### 3. 接続テスト
```bash
python -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://rea_user:rea_password@localhost/real_estate_db')
    print('✅ DB接続成功!')
    conn.close()
except Exception as e:
    print(f'❌ DB接続失敗: {{e}}')
"
```

### 4. shared/database.py 設定確認
```bash
#cd /Users/yaguchimakoto/my_programing/REA
code shared/database.py
# 認証情報が rea_user:rea_password になっているか確認
```

## 📋 既知のテーブル（エラー時参考）

| テーブル名 | 用途 | 推定カラム数 |
|------------|------|-------------|
| properties | 物件メイン情報 | 294 |
| equipment_master | 設備マスター | 10 |
| property_equipment | 物件-設備関連 | 6 |
| building_structure | 建物構造マスター | 6 |
| current_status | 現況マスター | 6 |
| property_types | 物件種別マスター | 6 |
| zoning_districts | 用途地域マスター | 6 |
| land_rights | 土地権利マスター | 6 |
| floor_plan_room_types | 間取りタイプマスター | 6 |
| image_types | 画像種別マスター | 6 |
| column_labels | カラムメタデータ | 13 |

## 🎯 次のアクション
1. 上記の対処方法を順番に実行
2. DB接続成功後に仕様書を再生成
3. `python main.py` を再実行

**エラー発生時刻**: {self.get_timestamp()}
"""

        # フォールバック仕様書を保存
        db_dir = self.get_output_dir("01_database")
        self.save_content(fallback_content, db_dir / "current_structure.md")

        return {"success": False, "error": error_message, "fallback_generated": True}

    def _get_table_purpose_auto(self, table_name: str) -> str:
        """テーブル用途を自動推定（ルールベース）"""

        # 既知テーブルの辞書（手動定義）
        known_purposes = {
            "properties": "物件メイン情報（294カラム・要分割）",
            "equipment_master": "設備マスター",
            "property_equipment": "物件-設備関連",
            "building_structure": "建物構造マスター",
            "current_status": "現況マスター",
            "property_types": "物件種別マスター",
            "zoning_districts": "用途地域マスター",
            "land_rights": "土地権利マスター",
            "floor_plan_room_types": "間取りタイプマスター",
            "image_types": "画像種別マスター",
            "column_labels": "カラムメタデータ",
            "properties_images": "画像情報（分割済み）",
            "properties_pricing": "価格情報（分割済み）",
            "properties_location": "所在地情報（分割済み）",
            "properties_building": "建物情報（分割済み）",
            "properties_contract": "契約情報（分割済み）",
            "properties_facilities": "周辺施設（分割済み）",
            "properties_transportation": "交通情報（分割済み）",
            "properties_roads": "接道情報（分割済み）",
            "properties_other": "その他情報（分割済み）",
            "properties_floor_plans": "間取り情報（分割済み）",
        }

        # 既知テーブルの場合
        if table_name in known_purposes:
            return known_purposes[table_name]

        # 🤖 新テーブルの自動推定
        return self._smart_guess_table_purpose(table_name)

    def _smart_guess_table_purpose(self, table_name: str) -> str:
        """スマート推定（ルールベース）"""
        try:
            from shared.database import READatabase

            table_info = READatabase.get_table_info(table_name)
            columns = table_info["columns"]
            record_count = table_info["record_count"]

            # パターンマッチング推定
            purpose = self._pattern_match_purpose(table_name, columns, record_count)
            return f"{purpose}（自動推定）"

        except Exception as e:
            return f"用途不明（新テーブル）"

    def _pattern_match_purpose(
        self, table_name: str, columns: list, record_count: int
    ) -> str:
        """パターンマッチングによる用途推定"""

        # テーブル名パターン推定
        name_patterns = {
            "_master": "マスターデータ",
            "_types": "種別マスター",
            "properties_": "プロパティ関連",
            "_equipment": "設備関連",
            "_log": "ログテーブル",
            "_history": "履歴テーブル",
            "_temp": "一時テーブル",
            "user_": "ユーザー関連",
            "admin_": "管理者関連",
            "_cache": "キャッシュテーブル",
            "_backup": "バックアップテーブル",
        }

        for pattern, purpose in name_patterns.items():
            if pattern in table_name:
                return purpose

        # カラム構成による推定
        if not columns:
            return "テーブル情報取得エラー"

        column_names = [col["column_name"].lower() for col in columns]

        # IDカラムパターン
        if "id" in column_names and len(columns) <= 10 and record_count < 1000:
            return "マスターテーブル"

        # 中間テーブルパターン
        fk_count = len([col for col in column_names if col.endswith("_id")])
        if fk_count >= 2:
            return "中間テーブル（多対多関係）"

        # ログテーブルパターン
        if "created_at" in column_names and (
            "log" in table_name.lower() or record_count > 1000
        ):
            return "ログテーブル"

        # 画像テーブルパターン
        image_keywords = ["image", "photo", "picture", "file_name", "url"]
        if any(
            word in col_name for col_name in column_names for word in image_keywords
        ):
            return "画像管理テーブル"

        # 価格テーブルパターン
        price_keywords = ["price", "cost", "fee", "amount", "rent"]
        if any(
            word in col_name for col_name in column_names for word in price_keywords
        ):
            return "価格・料金テーブル"

        # デフォルト推定
        if record_count == 0:
            return "新規作成テーブル（データなし）"
        elif record_count < 100:
            return "マスターデータ候補"
        elif record_count > 10000:
            return "大規模トランザクションテーブル"
        else:
            return "トランザクションデータ"

    def _get_table_insights(self, table_name: str) -> str:
        """テーブルの詳細洞察（オプション機能）"""
        try:
            from shared.database import READatabase

            table_info = READatabase.get_table_info(table_name)
            columns = table_info["columns"]
            record_count = table_info["record_count"]

            insights = []

            # データ量判定
            if record_count == 0:
                insights.append("📝 新規テーブル")
            elif record_count < 100:
                insights.append("📊 小規模データ")
            elif record_count > 10000:
                insights.append("🔥 大規模データ")

            # 特殊カラム検出
            if not columns:
                return "分析エラー"

            column_names = [col["column_name"].lower() for col in columns]
            if "created_at" in column_names:
                insights.append("⏰ タイムスタンプ管理")
            if any("json" in col.get("data_type", "").lower() for col in columns):
                insights.append("📋 JSON型使用")

            return " | ".join(insights) if insights else "標準テーブル"

        except Exception:
            return "洞察取得エラー"
