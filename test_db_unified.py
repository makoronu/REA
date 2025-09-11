#!/usr/bin/env python3
"""DB接続統一化テストスクリプト"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("🔍 DB接続テスト開始...")

# 1. shared/database.pyのテスト
print("\n1️⃣ shared/database.py テスト")
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

# 2. rea-apiのテスト（モジュール名にハイフンは使えないのでスキップ）
print("\n2️⃣ rea-api データベース接続テスト")
print("  ⏭️  スキップ（rea-apiはFastAPI起動時にテスト）")

print("\n✅ テスト完了")
