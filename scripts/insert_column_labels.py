"""
column_labelsテーブルに日本語ラベルを登録するスクリプト
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.database import READatabase

# propertiesテーブルのラベル定義
properties_labels = [
    # 基本情報
    ('properties', 'id', 'ID', '物件ID', 'integer', True, 1, '基本情報', 'hidden'),
    ('properties', 'homes_record_id', 'ホームズ物件ID', 'ホームズサイトの物件識別ID', 'text', False, 2, '基本情報', 'text'),
    ('properties', 'company_property_number', '自社物件番号', '会社独自の物件管理番号', 'text', False, 3, '基本情報', 'text'),
    ('properties', 'status', 'ステータス', '物件の状態（公開/非公開など）', 'text', False, 4, '基本情報', 'select'),
    ('properties', 'property_type', '物件種別', 'マンション、戸建て、土地など', 'text', True, 5, '基本情報', 'select'),
    ('properties', 'investment_property', '投資物件', '投資用物件かどうか', 'text', False, 6, '基本情報', 'checkbox'),
    
    # 建物情報
    ('properties', 'building_property_name', '物件名', '建物やマンションの名称', 'text', True, 10, '建物情報', 'text'),
    ('properties', 'building_name_kana', '物件名カナ', '物件名のカナ表記', 'text', False, 11, '建物情報', 'text'),
    ('properties', 'property_name_public', '公開物件名', '一般公開する物件名', 'text', False, 12, '建物情報', 'checkbox'),
    ('properties', 'total_units', '総戸数', '建物全体の戸数', 'integer', False, 13, '建物情報', 'number'),
    ('properties', 'vacant_units', '空室数', '現在の空室数', 'integer', False, 14, '建物情報', 'number'),
    ('properties', 'vacant_units_detail', '空室詳細', '空室の詳細情報', 'text', False, 15, '建物情報', 'textarea'),
    
    # ID関連
    ('properties', 'building_structure_id', '建物構造ID', '建物構造の識別ID', 'text', False, 20, 'ID情報', 'text'),
    ('properties', 'current_status_id', '現況ID', '現在の状態を示すID', 'text', False, 21, 'ID情報', 'text'),
    ('properties', 'property_type_id', '物件タイプID', '物件タイプの識別ID', 'text', False, 22, 'ID情報', 'text'),
    ('properties', 'zoning_district_id', '用途地域ID', '用途地域の識別ID', 'text', False, 23, 'ID情報', 'text'),
    ('properties', 'land_rights_id', '土地権利ID', '土地権利形態の識別ID', 'text', False, 24, 'ID情報', 'text'),
    
    # システム情報
    ('properties', 'created_at', '作成日時', 'レコード作成日時', 'datetime', True, 98, 'システム', 'datetime'),
    ('properties', 'updated_at', '更新日時', '最終更新日時', 'datetime', True, 99, 'システム', 'datetime'),
]

def insert_labels():
    """ラベルをデータベースに登録"""
    
    # 直接接続を取得してコミットを制御
    conn = READatabase.get_connection()
    if not conn:
        print("データベース接続に失敗しました")
        return
    
    try:
        cursor = conn.cursor()
        
        # まず既存のpropertiesテーブルのラベルを削除
        delete_query = "DELETE FROM column_labels WHERE table_name = 'properties'"
        cursor.execute(delete_query)
        print("既存のpropertiesラベルを削除しました")
        
        # 新しいラベルを挿入
        insert_query = """
            INSERT INTO column_labels (
                table_name, column_name, japanese_label, description, 
                data_type, is_required, display_order, group_name, input_type
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        inserted_count = 0
        for label_data in properties_labels:
            try:
                cursor.execute(insert_query, label_data)
                inserted_count += 1
                print(f"✓ {label_data[1]}: {label_data[2]}")
            except Exception as e:
                print(f"✗ {label_data[1]}: エラー - {str(e)}")
        
        # コミット
        conn.commit()
        print(f"\n合計 {inserted_count} 件のラベルを登録しました（コミット済み）")
        
    except Exception as e:
        conn.rollback()
        print(f"エラーが発生しました: {str(e)}")
    finally:
        cursor.close()
        conn.close()
    
    # 登録結果を確認
    result = READatabase.execute_query_dict("""
        SELECT column_name, japanese_label, group_name 
        FROM column_labels 
        WHERE table_name = 'properties' 
        ORDER BY display_order
    """)
    
    print("\n登録されたラベル:")
    current_group = None
    for row in result:
        if row['group_name'] != current_group:
            current_group = row['group_name']
            print(f"\n【{current_group}】")
        print(f"  - {row['column_name']}: {row['japanese_label']}")

if __name__ == "__main__":
    print("column_labelsテーブルへのラベル登録を開始します...")
    
    # 接続テスト
    if READatabase.test_connection():
        print("データベース接続成功")
        insert_labels()
        
        # 登録結果を確認
        result = READatabase.execute_query_dict("""
            SELECT column_name, japanese_label, group_name 
            FROM column_labels 
            WHERE table_name = 'properties' 
            ORDER BY display_order
        """)
        
        if result:
            print("\n登録されたラベル:")
            current_group = None
            for row in result:
                if row['group_name'] != current_group:
                    current_group = row['group_name']
                    print(f"\n【{current_group}】")
                print(f"  - {row['column_name']}: {row['japanese_label']}")
        else:
            print("\nラベルが登録されていません")
    else:
        print("データベース接続失敗")
        exit(1)