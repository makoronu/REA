#!/usr/bin/env python3
"""
CSVファイルから全properties系テーブルの日本語ラベルを登録するスクリプト
"""
import csv
from shared.database import READatabase
from datetime import datetime

def main():
    db = READatabase()
    
    # CSVファイルを読み込み
    csv_file = 'data/property_columns_master.csv'
    
    # まず現在のテーブル構造を取得
    tables = [t for t in db.get_all_tables() if t.startswith('properties')]
    table_columns = {}
    
    print("📊 現在のテーブル構造を取得中...")
    for table in tables:
        info = db.get_table_info(table)
        columns = [col['column_name'] for col in info['columns']]
        table_columns[table] = columns
        print(f"  {table}: {len(columns)}カラム")
    
    # CSVを読み込んでマッピング
    print("\n📖 CSVファイルを読み込み中...")
    column_mappings = {}  # {column_name: (japanese_label, description, data_type, enum_values)}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['internal_id'] and row['項目名']:
                column_mappings[row['internal_id']] = {
                    'japanese_label': row['項目名'],
                    'description': row.get('説明', ''),
                    'data_type': row.get('データ型', ''),
                    'enum_values': row.get('選択肢', '')
                }
    
    print(f"  {len(column_mappings)}個のカラム定義を読み込みました")
    
    # 各テーブルごとに処理
    total_inserted = 0
    conn = db.get_connection()
    cur = conn.cursor()
    
    try:
        for table in sorted(tables):
            print(f"\n🔧 {table} の処理中...")
            
            # 既存のラベルを削除（更新のため）
            cur.execute("DELETE FROM column_labels WHERE table_name = %s", (table,))
            
            inserted = 0
            for idx, column_name in enumerate(table_columns[table]):
                # id と property_id は特別扱い
                if column_name == 'id':
                    japanese_label = 'ID'
                    description = 'プライマリキー'
                elif column_name == 'property_id':
                    japanese_label = '物件ID'
                    description = 'propertiesテーブルへの外部キー'
                elif column_name == 'created_at':
                    japanese_label = '作成日時'
                    description = 'レコード作成日時'
                elif column_name == 'updated_at':
                    japanese_label = '更新日時'
                    description = 'レコード更新日時'
                else:
                    # CSVから情報を取得
                    if column_name in column_mappings:
                        info = column_mappings[column_name]
                        japanese_label = info['japanese_label']
                        description = info['description']
                    else:
                        # マッピングが見つからない場合はスキップ
                        print(f"  ⚠️  {column_name} のマッピングが見つかりません")
                        continue
                
                # column_labelsに挿入
                insert_query = """
                INSERT INTO column_labels (
                    table_name, column_name, japanese_label, description,
                    display_order, group_name, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # グループ名を決定
                group_name = get_group_name(table)
                
                cur.execute(insert_query, (
                    table, column_name, japanese_label, description,
                    idx + 1, group_name, datetime.now(), datetime.now()
                ))
                inserted += 1
            
            conn.commit()
            print(f"  ✅ {inserted}件のラベルを登録しました")
            total_inserted += inserted
            
    except Exception as e:
        conn.rollback()
        print(f"\n❌ エラーが発生しました: {e}")
        raise
    finally:
        cur.close()
        conn.close()
    
    print(f"\n🎉 合計 {total_inserted} 件のラベルを登録しました！")
    
    # 登録状況を確認
    print("\n📊 最終的な登録状況:")
    for table in sorted(tables):
        result = db.execute_query(
            "SELECT COUNT(*) FROM column_labels WHERE table_name = %s",
            (table,)
        )
        count = result[0][0] if result else 0
        total = len(table_columns[table])
        percentage = (count / total * 100) if total > 0 else 0
        status = '✅' if percentage == 100 else '⚠️' if percentage > 0 else '❌'
        print(f"{status} {table:30s}: {count:3d}/{total:3d} ({percentage:5.1f}%)")

def get_group_name(table_name):
    """テーブル名からグループ名を決定"""
    group_mappings = {
        'properties': '基本情報',
        'properties_location': '所在地情報',
        'properties_pricing': '価格情報',
        'properties_building': '建物情報',
        'properties_contract': '契約情報',
        'properties_facilities': '周辺施設',
        'properties_floor_plans': '間取り情報',
        'properties_images': '画像情報',
        'properties_roads': '接道情報',
        'properties_transportation': '交通情報',
        'properties_other': 'その他情報'
    }
    return group_mappings.get(table_name, 'その他')

if __name__ == "__main__":
    main()