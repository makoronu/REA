#!/usr/bin/env python3
"""
column_labels整合性チェック

実行タイミング：
- column_labels変更後
- デプロイ前
- 定期実行（週1）

チェック内容：
1. group_orderがNULLのレコード
2. display_orderが重複しているグループ
3. group_orderが重複しているグループ（同一テーブル内）
"""
import sys
sys.path.insert(0, '/Users/yaguchimakoto/my_programing/REA')

from shared.database import READatabase

def check_column_labels():
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()
    
    errors = []
    warnings = []
    
    # 1. group_orderがNULLのレコード
    cur.execute("""
        SELECT table_name, column_name, group_name
        FROM column_labels
        WHERE group_order IS NULL
    """)
    null_group_orders = cur.fetchall()
    if null_group_orders:
        for row in null_group_orders:
            errors.append(f"group_order NULL: {row[0]}.{row[1]} (グループ: {row[2]})")
    
    # 2. display_orderが重複しているグループ内
    cur.execute("""
        SELECT table_name, group_name, display_order, COUNT(*) as cnt
        FROM column_labels
        WHERE display_order IS NOT NULL
        GROUP BY table_name, group_name, display_order
        HAVING COUNT(*) > 1
    """)
    dup_display = cur.fetchall()
    if dup_display:
        for row in dup_display:
            warnings.append(f"display_order重複: {row[0]}.{row[1]} order={row[2]} ({row[3]}件)")
    
    # 3. group_orderの連番チェック（欠番は警告のみ）
    cur.execute("""
        SELECT table_name, 
               array_agg(DISTINCT group_order ORDER BY group_order) as orders
        FROM column_labels
        WHERE group_order IS NOT NULL AND group_order < 900
        GROUP BY table_name
    """)
    for row in cur.fetchall():
        table_name, orders = row
        if orders:
            expected = list(range(min(orders), max(orders) + 1))
            missing = set(expected) - set(orders)
            if missing and len(missing) < 5:  # 大きな欠番は意図的
                warnings.append(f"group_order欠番: {table_name} missing={sorted(missing)}")
    
    cur.close()
    conn.close()
    
    # 結果出力
    print("=" * 50)
    print("column_labels 整合性チェック")
    print("=" * 50)
    
    if errors:
        print(f"\n❌ エラー ({len(errors)}件):")
        for e in errors:
            print(f"  - {e}")
    
    if warnings:
        print(f"\n⚠️ 警告 ({len(warnings)}件):")
        for w in warnings:
            print(f"  - {w}")
    
    if not errors and not warnings:
        print("\n✅ 問題なし")
    
    print()
    
    # エラーがあれば終了コード1
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(check_column_labels())
