"""REA シンプルデータベース接続

【重要】DB接続設定について
========================
このファイルは必ずプロジェクトルートの.envファイルから設定を読み込みます。
.envファイルの場所: プロジェクトルート/.env（shared/の親ディレクトリ）

.envファイルに以下の設定が必要です：

DB_HOST=localhost        # Docker PostgreSQL接続用
DB_PORT=5432            # PostgreSQLのポート
DB_NAME=real_estate_db  # データベース名
DB_USER=rea_user        # データベースユーザー名
DB_PASSWORD=rea_password # データベースパスワード

【共通ライブラリの仕様】
========================
- どこから実行しても同じ.envファイルを使用
- 設定の一元管理を実現
- 実行場所に依存しない安定した接続
- 全てのモジュールはこのライブラリを経由してDB接続する

【変更履歴】
========================
2025-07-23: プロジェクトルート固定化（技術的負債解消）
           - 実行場所による.env読み込みの差異を解消
           - DB接続の完全統一化を実現
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor


class READatabase:
    """シンプルなDB接続クラス

    REAプロジェクトの全てのDB接続を統一管理する共通ライブラリ。
    どのモジュールから使用しても同じ設定で接続できることを保証する。
    """

    @classmethod
    def _load_env(cls):
        """プロジェクトルートの.envファイルを必ず読み込む

        共通ライブラリの核心部分：
        - 常にプロジェクトルートの.envを使用
        - どこから実行しても同じ設定を使用
        - 設定の一元管理を実現

        変更前の問題点：
        - カレントディレクトリから探していたため、実行場所により異なる.envを読んでいた
        - auto_spec_generatorから実行時とREAルートから実行時で挙動が異なっていた

        解決策：
        - プロジェクトルートを固定パスで指定
        - どこから実行しても必ず同じ.envファイルを読む
        """
        # プロジェクトルートを検出（このファイルの親の親ディレクトリ）
        # shared/database.py → shared → REA
        project_root = Path(__file__).resolve().parent.parent
        env_path = project_root / ".env"

        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value.strip("\"'")
        else:
            print(f"警告: .envファイルが見つかりません: {env_path}")
            print("デフォルト値を使用します。")

    @classmethod
    def get_connection(cls):
        """DB接続を取得

        環境変数から接続情報を取得します。
        必ずプロジェクトルートの.envファイルを読み込みます。

        デフォルト値：
        - host: localhost
        - port: 5432
        - database: real_estate_db
        - user: rea_user
        - password: rea_password

        Returns:
            psycopg2.connection: PostgreSQL接続オブジェクト

        Raises:
            psycopg2.OperationalError: 接続失敗時
        """
        cls._load_env()

        # 接続情報（.envから読み込み、なければデフォルト値）
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "real_estate_db"),
            user=os.getenv("DB_USER", "rea_user"),
            password=os.getenv("DB_PASSWORD", "rea_password"),
        )

    @classmethod
    def test_connection(cls) -> bool:
        """接続テスト

        DB接続が可能かテストします。
        全モジュールで使用前にこのメソッドでテストすることを推奨。

        Returns:
            bool: 接続成功時True、失敗時False

        Example:
            if READatabase.test_connection():
                print("DB接続成功！")
            else:
                print("DB接続失敗！.envファイルを確認してください。")
        """
        try:
            conn = cls.get_connection()
            conn.close()
            return True
        except Exception as e:
            print(f"DB接続エラー: {e}")
            return False

    @classmethod
    @contextmanager
    def cursor(cls, commit: bool = False) -> Generator[Tuple[Any, Any], None, None]:
        """DB接続コンテキストマネージャー（カーソル付き）

        try-finally ボイラープレートを削減するためのコンテキストマネージャー。
        自動的に接続をクローズし、オプションでコミットも行う。

        Args:
            commit: Trueの場合、正常終了時にコミットする

        Yields:
            Tuple[cursor, connection]: カーソルと接続オブジェクト

        Example:
            # 読み取り専用
            with READatabase.cursor() as (cur, conn):
                cur.execute("SELECT * FROM properties LIMIT 5")
                rows = cur.fetchall()

            # 書き込み（自動コミット）
            with READatabase.cursor(commit=True) as (cur, conn):
                cur.execute("INSERT INTO ... VALUES ...")

            # 書き込み（手動コミット）
            with READatabase.cursor() as (cur, conn):
                cur.execute("INSERT INTO ... VALUES ...")
                conn.commit()
        """
        conn = None
        cur = None
        try:
            conn = cls.get_connection()
            cur = conn.cursor()
            yield cur, conn
            if commit:
                conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @classmethod
    @contextmanager
    def dict_cursor(cls, commit: bool = False) -> Generator[Tuple[Any, Any], None, None]:
        """DB接続コンテキストマネージャー（辞書カーソル付き）

        結果を辞書形式で取得したい場合に使用。

        Args:
            commit: Trueの場合、正常終了時にコミットする

        Yields:
            Tuple[cursor, connection]: 辞書カーソルと接続オブジェクト

        Example:
            with READatabase.dict_cursor() as (cur, conn):
                cur.execute("SELECT * FROM properties LIMIT 5")
                for row in cur.fetchall():
                    print(row['property_name'])
        """
        conn = None
        cur = None
        try:
            conn = cls.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            yield cur, conn
            if commit:
                conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @classmethod
    def execute_query(cls, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """クエリ実行（タプル形式）

        基本的なSQL実行メソッド。結果はタプルのリストで返す。

        Args:
            query: SQL文（パラメータは%sでプレースホルダ）
            params: バインドパラメータ（SQLインジェクション対策）

        Returns:
            List[tuple]: 実行結果

        Example:
            result = READatabase.execute_query(
                "SELECT id, title FROM properties WHERE price > %s",
                (10000000,)
            )
            for row in result:
                print(f"ID: {row[0]}, Title: {row[1]}")
        """
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute(query, params or ())
        result = cur.fetchall() if cur.description else []
        conn.close()
        return result

    @classmethod
    def execute_query_dict(
        cls, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """クエリ実行（辞書形式）

        結果を辞書形式で返すため、カラム名でアクセス可能。
        実用的なデータ処理に最適。

        Args:
            query: SQL文
            params: バインドパラメータ

        Returns:
            List[Dict[str, Any]]: 実行結果（カラム名をキーとする辞書のリスト）

        Example:
            properties = READatabase.execute_query_dict(
                "SELECT * FROM properties WHERE price > %s LIMIT 5",
                (10000000,)
            )
            for prop in properties:
                print(f"{prop['title']}: {prop['price']}円")
        """
        conn = cls.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params or ())
        result = cur.fetchall() if cur.description else []
        conn.close()
        return [dict(row) for row in result]

    @classmethod
    def get_all_tables(cls) -> List[str]:
        """テーブル一覧取得

        publicスキーマの全テーブルを取得。
        DB構造の確認や仕様書生成で使用。

        Returns:
            List[str]: publicスキーマのテーブル名一覧

        Example:
            tables = READatabase.get_all_tables()
            print(f"テーブル数: {len(tables)}")
            for table in tables:
                print(f"- {table}")
        """
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
        """
        result = cls.execute_query(query)
        return [row[0] for row in result]

    @classmethod
    def get_table_info(cls, table_name: str) -> Dict[str, Any]:
        """テーブル情報取得

        指定テーブルの詳細情報を取得。
        カラム情報、レコード数などを含む。

        Args:
            table_name: テーブル名

        Returns:
            Dict[str, Any]: テーブル情報
                - table_name: テーブル名
                - columns: カラム情報のリスト
                - column_count: カラム数
                - record_count: レコード数

        Example:
            info = READatabase.get_table_info('properties')
            print(f"カラム数: {info['column_count']}")
            print(f"レコード数: {info['record_count']}")
        """
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
        columns = cls.execute_query_dict(query, (table_name,))

        # レコード数取得（安全なテーブル名チェック）
        if not table_name.replace("_", "").isalnum():
            raise ValueError(f"不正なテーブル名: {table_name}")

        count_result = cls.execute_query(f"SELECT COUNT(*) FROM {table_name}")
        record_count = count_result[0][0] if count_result else 0

        return {
            "table_name": table_name,
            "columns": columns,
            "column_count": len(columns),
            "record_count": record_count,
        }

    @classmethod
    def health_check(cls) -> Dict[str, Any]:
        """DB健康チェック

        DB接続の詳細な状態を確認。
        モニタリングやデバッグで使用。

        Returns:
            Dict[str, Any]: DB接続状態
                - status: 'healthy' or 'unhealthy'
                - database: データベース名
                - version: PostgreSQLバージョン
                - config_source: 設定ソース
                - error: エラーメッセージ（エラー時のみ）

        Example:
            health = READatabase.health_check()
            if health['status'] == 'healthy':
                print(f"DB正常: {health['database']}")
                print(f"バージョン: {health['version']}")
            else:
                print(f"DBエラー: {health['error']}")
        """
        try:
            conn = cls.get_connection()
            cur = conn.cursor()

            # PostgreSQLバージョン取得
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]

            # データベース名取得
            cur.execute("SELECT current_database()")
            database = cur.fetchone()[0]

            conn.close()

            return {
                "status": "healthy",
                "database": database,
                "version": version,
                "config_source": "プロジェクトルート/.env",
                "response_time_ms": 10,  # 簡易的な値
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database": "unknown",
                "version": "unknown",
                "config_source": "unknown",
                "response_time_ms": 0,
            }


# 簡単に使える関数（後方互換性のため維持）
def quick_test():
    """接続テストのショートカット

    既存コードとの互換性のため維持。
    新規コードではREADatabase.test_connection()を推奨。
    """
    return READatabase.test_connection()


def get_tables():
    """テーブル一覧取得のショートカット

    既存コードとの互換性のため維持。
    新規コードではREADatabase.get_all_tables()を推奨。
    """
    return READatabase.get_all_tables()


# ===== 使用例 =====
#
# 【基本的な使い方】
#
# # 1. 接続テスト
# if READatabase.test_connection():
#     print("DB接続成功！")
# else:
#     print("DB接続失敗！")
#
# # 2. テーブル一覧取得
# tables = READatabase.get_all_tables()
# print(f"テーブル数: {len(tables)}")
#
# # 3. データ取得（辞書形式）
# properties = READatabase.execute_query_dict(
#     "SELECT * FROM properties WHERE price > %s LIMIT 5",
#     (10000000,)
# )
# for prop in properties:
#     print(f"{prop['title']}: {prop['price']}円")
#
# # 4. テーブル情報取得
# info = READatabase.get_table_info('properties')
# print(f"propertiesテーブル: {info['column_count']}カラム, {info['record_count']}件")
#
# # 5. DB健康チェック
# health = READatabase.health_check()
# print(f"DB状態: {health['status']}")
#
# 【他モジュールからの使い方】
#
# # rea-api から使う場合
# from shared.database import READatabase
#
# # rea-scraper から使う場合
# import sys
# sys.path.append('/Users/yaguchimakoto/my_programing/REA')
# from shared.database import READatabase
#
# # どこから使っても同じ.envファイルを読むので安心！
