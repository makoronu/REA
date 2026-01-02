#!/usr/bin/env python3
"""
プロトコル準拠チェッカー

実行: python scripts/check_protocol.py

チェック項目:
1. 全テーブルに必須カラム（created_at, updated_at, created_by, updated_by, deleted_at）があるか
2. ENUM型が使用されていないか
3. SELECT * がコードに含まれていないか
4. 例外握りつぶし（except: pass）がないか
"""

import os
import sys
import re
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

import psycopg2


def check_audit_columns():
    """必須カラムチェック"""
    print("=" * 60)
    print("1. 必須カラムチェック")
    print("=" * 60)

    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()

    # 除外テーブル（一時テーブルなど）
    excluded_tables = ['password_reset_tokens', 'zoho_import_staging', 'spatial_ref_sys']

    cur.execute('''
        SELECT
            t.table_name,
            array_agg(c.column_name ORDER BY c.ordinal_position) as columns
        FROM information_schema.tables t
        JOIN information_schema.columns c ON t.table_name = c.table_name AND t.table_schema = c.table_schema
        WHERE t.table_schema = 'public'
        AND t.table_type = 'BASE TABLE'
        GROUP BY t.table_name
        ORDER BY t.table_name
    ''')

    required = ['created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_at']
    violations = []

    for row in cur.fetchall():
        table_name = row[0]
        columns = row[1]

        if table_name in excluded_tables:
            continue

        missing = [col for col in required if col not in columns]
        if missing:
            violations.append((table_name, missing))

    cur.close()
    conn.close()

    if violations:
        print(f"❌ 違反: {len(violations)}テーブル")
        for table, missing in violations:
            print(f"   - {table}: {missing}")
        return False
    else:
        print("✅ 全テーブル準拠")
        return True


def check_enum_types():
    """ENUM型チェック"""
    print()
    print("=" * 60)
    print("2. ENUM型チェック")
    print("=" * 60)

    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()

    cur.execute('''
        SELECT t.typname
        FROM pg_type t
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE t.typtype = 'e'
        AND n.nspname = 'public'
    ''')

    enums = cur.fetchall()
    cur.close()
    conn.close()

    if enums:
        print(f"❌ 違反: {len(enums)}個のENUM型")
        for enum in enums:
            print(f"   - {enum[0]}")
        return False
    else:
        print("✅ ENUM型なし")
        return True


def check_select_star():
    """SELECT * チェック"""
    print()
    print("=" * 60)
    print("3. SELECT * チェック")
    print("=" * 60)

    api_dir = project_root / "rea-api" / "app"
    pattern = re.compile(r'SELECT\s+\*\s+FROM', re.IGNORECASE)
    violations = []

    for py_file in api_dir.rglob("*.py"):
        try:
            content = py_file.read_text()
            matches = pattern.findall(content)
            if matches:
                # 行番号を特定
                for i, line in enumerate(content.split('\n'), 1):
                    if pattern.search(line):
                        violations.append((py_file.relative_to(project_root), i))
        except Exception:
            continue

    if violations:
        print(f"❌ 違反: {len(violations)}箇所")
        for file, line in violations:
            print(f"   - {file}:{line}")
        return False
    else:
        print("✅ SELECT * なし")
        return True


def check_exception_swallowing():
    """例外握りつぶしチェック"""
    print()
    print("=" * 60)
    print("4. 例外握りつぶしチェック")
    print("=" * 60)

    api_dir = project_root / "rea-api" / "app"
    pattern = re.compile(r'except\s*:\s*pass', re.IGNORECASE)
    violations = []

    for py_file in api_dir.rglob("*.py"):
        try:
            content = py_file.read_text()
            for i, line in enumerate(content.split('\n'), 1):
                if pattern.search(line):
                    violations.append((py_file.relative_to(project_root), i, line.strip()))
        except Exception:
            continue

    if violations:
        print(f"❌ 違反: {len(violations)}箇所")
        for file, line, code in violations:
            print(f"   - {file}:{line}")
        return False
    else:
        print("✅ 例外握りつぶしなし")
        return True


def check_physical_delete():
    """物理削除チェック（DELETE FROM）"""
    print()
    print("=" * 60)
    print("5. 物理削除チェック")
    print("=" * 60)

    api_dir = project_root / "rea-api" / "app"
    pattern = re.compile(r'DELETE\s+FROM\s+\w+\s+WHERE', re.IGNORECASE)
    violations = []

    # 除外パターン（テスト用、一時テーブルなど）
    exclude_patterns = ['zoho_import_staging', 'password_reset_tokens']

    for py_file in api_dir.rglob("*.py"):
        try:
            content = py_file.read_text()
            for i, line in enumerate(content.split('\n'), 1):
                if pattern.search(line):
                    # 除外テーブルはスキップ
                    if any(exc in line for exc in exclude_patterns):
                        continue
                    violations.append((py_file.relative_to(project_root), i, line.strip()[:60]))
        except Exception:
            continue

    if violations:
        print(f"❌ 違反: {len(violations)}箇所")
        for file, line, code in violations:
            print(f"   - {file}:{line}")
            print(f"     {code}...")
        return False
    else:
        print("✅ 物理削除なし")
        return True


def main():
    print()
    print("╔" + "═" * 58 + "╗")
    print("║       REA プロトコル準拠チェッカー                     ║")
    print("╚" + "═" * 58 + "╝")
    print()

    results = []
    results.append(("必須カラム", check_audit_columns()))
    results.append(("ENUM型", check_enum_types()))
    results.append(("SELECT *", check_select_star()))
    results.append(("例外握りつぶし", check_exception_swallowing()))
    results.append(("物理削除", check_physical_delete()))

    print()
    print("=" * 60)
    print("総合結果")
    print("=" * 60)

    all_passed = all(r[1] for r in results)

    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"  {status} {name}")

    print()
    if all_passed:
        print("🎉 全チェック合格 - デプロイ可能")
        return 0
    else:
        print("⚠️  違反あり - 修正が必要")
        return 1


if __name__ == "__main__":
    sys.exit(main())
