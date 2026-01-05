#!/usr/bin/env python3
"""
required_for_publication設定のデバッグ
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rea-api'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 本番DB接続
DATABASE_URL = "postgresql://rea_user:rea_password@realestateautomation.net:5432/real_estate_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    # 1. 土地物件のproperty_type値を確認
    print("=" * 60)
    print("1. 土地物件のproperty_type値")
    print("=" * 60)
    result = db.execute(text("""
        SELECT id, property_name, property_type, sales_status, publication_status
        FROM properties
        WHERE property_type LIKE '%land%' OR property_type LIKE '%土地%' OR property_type = 'detached'
        LIMIT 10
    """))
    for row in result:
        print(f"ID: {row.id}, type: {row.property_type}, sales: {row.sales_status}, pub: {row.publication_status}")

    # 2. property_typesテーブルの内容
    print("\n" + "=" * 60)
    print("2. property_typesテーブル（土地関連）")
    print("=" * 60)
    result = db.execute(text("""
        SELECT id, label, group_name
        FROM property_types
        WHERE label LIKE '%土地%' OR id LIKE '%land%' OR id = 'detached'
    """))
    for row in result:
        print(f"ID: {row.id}, label: {row.label}, group: {row.group_name}")

    # 3. required_for_publicationの設定一覧
    print("\n" + "=" * 60)
    print("3. required_for_publication設定一覧")
    print("=" * 60)
    result = db.execute(text("""
        SELECT table_name, column_name, japanese_label, required_for_publication
        FROM column_labels
        WHERE required_for_publication IS NOT NULL
          AND required_for_publication != '{}'
        ORDER BY table_name, column_name
    """))
    for row in result:
        print(f"{row.table_name}.{row.column_name}: {row.japanese_label} -> {row.required_for_publication}")

    # 4. 具体的な土地物件でテスト
    print("\n" + "=" * 60)
    print("4. property 1908のproperty_type確認")
    print("=" * 60)
    result = db.execute(text("""
        SELECT id, property_type, sales_status, publication_status
        FROM properties
        WHERE id = 1908
    """)).fetchone()
    if result:
        print(f"property_type = '{result.property_type}'")

        # このproperty_typeで必須になるフィールドを取得
        print(f"\n必須フィールド (property_type = '{result.property_type}'):")
        req_result = db.execute(text("""
            SELECT table_name, column_name, japanese_label, required_for_publication
            FROM column_labels
            WHERE required_for_publication IS NOT NULL
              AND :property_type = ANY(required_for_publication)
            ORDER BY table_name, column_name
        """), {"property_type": result.property_type})
        count = 0
        for row in req_result:
            count += 1
            print(f"  {count}. {row.table_name}.{row.column_name}: {row.japanese_label}")
        print(f"\n合計: {count}件")

finally:
    db.close()
