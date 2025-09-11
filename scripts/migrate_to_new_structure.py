#!/usr/bin/env python3
"""
REA データベース構造変更スクリプト
11テーブル → 5テーブルへの再構成
"""

import sys

sys.path.append(".")
import json
from datetime import datetime

from shared.database import READatabase


def main():
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        print("🚀 REA データベース構造変更開始...")
        print(f"⏰ 開始時刻: {datetime.now()}")

        # 1. 既存テーブルのバックアップ（念のため）
        print("\n📦 既存テーブルの状態を保存...")
        backup_existing_structure(cur)

        # 2. 既存のプロパティ系テーブルを削除
        print("\n🗑️ 既存テーブルを削除...")
        drop_existing_tables(cur)

        # 3. 新しいENUM型の作成（テーブル作成前に必要）
        print("\n🔧 ENUM型を作成...")
        create_enum_types(cur)

        # 4. 新しいテーブル構造を作成
        print("\n🏗️ 新しいテーブル構造を作成...")
        create_new_tables(cur)

        # 5. column_labelsテーブルのデータを削除（新構造に合わせて再登録が必要）
        print("\n🧹 column_labelsをクリア...")
        cur.execute("DELETE FROM column_labels WHERE table_name LIKE 'properties%'")

        # コミット
        conn.commit()
        print("\n✅ データベース構造変更完了！")

        # 6. 新しいテーブル構造を確認
        print("\n📊 新しいテーブル構造:")
        show_new_structure(db)

    except Exception as e:
        conn.rollback()
        print(f"\n❌ エラー: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def backup_existing_structure(cur):
    """既存構造のバックアップ（情報のみ）"""
    cur.execute(
        """
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'properties%'
        ORDER BY table_name, ordinal_position
    """
    )

    with open("backup_table_structure.json", "w", encoding="utf-8") as f:
        json.dump(cur.fetchall(), f, ensure_ascii=False, indent=2)
    print("  ✅ 構造情報をbackup_table_structure.jsonに保存")


def drop_existing_tables(cur):
    """既存のプロパティ系テーブルを削除"""
    tables = [
        "properties_images",
        "properties_transportation",
        "properties_roads",
        "properties_pricing",
        "properties_other",
        "properties_location",
        "properties_floor_plans",
        "properties_facilities",
        "properties_contract",
        "properties_building",
        "properties",
    ]

    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        print(f"  ✅ {table} 削除完了")


def create_enum_types(cur):
    """ENUM型の作成"""
    # 既存のENUM型を削除
    cur.execute("DROP TYPE IF EXISTS property_type_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS investment_property_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS sales_status_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS publication_status_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS price_status_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS current_status_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS delivery_timing_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS transaction_type_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS land_area_measurement_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS use_district_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS land_rights_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS setback_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS land_transaction_notice_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS building_structure_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS area_measurement_type_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS direction_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS room_type_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS management_type_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS management_association_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS building_manager_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS parking_availability_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS parking_type_enum CASCADE")
    cur.execute("DROP TYPE IF EXISTS image_type_enum CASCADE")

    # 新しいENUM型を作成
    enums = {
        "property_type_enum": "('1:マンション', '2:一戸建て', '3:土地', '4:その他')",
        "investment_property_enum": "('0:実需', '1:投資')",
        "sales_status_enum": "('1:販売中', '2:商談中', '3:成約済み', '4:販売終了')",
        "publication_status_enum": "('1:公開', '2:非公開', '3:限定公開')",
        "price_status_enum": "('1:確定', '2:相談', '3:応相談')",
        "current_status_enum": "('1:空家', '2:居住中', '3:賃貸中', '9:その他')",
        "delivery_timing_enum": "('1:即時', '2:相談', '3:期日指定')",
        "transaction_type_enum": "('1:売主', '2:代理', '3:専任媒介', '4:一般媒介', '5:専属専任')",
        "land_area_measurement_enum": "('1:公簿', '2:実測', '3:私測')",
        "use_district_enum": "('1:第一種低層住居専用', '2:第二種低層住居専用', '3:第一種中高層住居専用', '4:第二種中高層住居専用', '5:第一種住居', '6:第二種住居', '7:準住居', '8:近隣商業', '9:商業', '10:準工業', '11:工業', '12:工業専用')",
        "land_rights_enum": "('1:所有権', '2:借地権', '3:定期借地権', '4:地上権')",
        "setback_enum": "('0:不要', '1:要', '2:セットバック済')",
        "land_transaction_notice_enum": "('0:不要', '1:要', '2:届出済')",
        "building_structure_enum": "('1:木造', '2:鉄骨造', '3:RC造', '4:SRC造', '5:軽量鉄骨', '6:ALC', '9:その他')",
        "area_measurement_type_enum": "('1:壁芯', '2:内法', '3:登記簿')",
        "direction_enum": "('1:北', '2:北東', '3:東', '4:南東', '5:南', '6:南西', '7:西', '8:北西')",
        "room_type_enum": "('1:R', '2:K', '3:DK', '4:LDK', '5:SLDK', '6:その他')",
        "management_type_enum": "('1:自主管理', '2:管理会社委託', '3:一部委託', '9:その他')",
        "management_association_enum": "('0:無', '1:有')",
        "building_manager_enum": "('1:常駐', '2:日勤', '3:巡回', '4:自主管理', '9:無')",
        "parking_availability_enum": "('1:無', '2:有(無料)', '3:有(有料)', '4:近隣(無料)', '5:近隣(有料)')",
        "parking_type_enum": "('1:平置き', '2:機械式', '3:立体', '9:その他')",
        "image_type_enum": "('01:外観', '02:間取図', '03:居室', '04:キッチン', '05:風呂', '06:トイレ', '07:洗面', '08:設備', '09:玄関', '10:バルコニー', '11:眺望', '12:共用部', '13:周辺環境', '14:その他')",
    }

    for enum_name, values in enums.items():
        cur.execute(f"CREATE TYPE {enum_name} AS ENUM {values}")
        print(f"  ✅ {enum_name} 作成完了")


def create_new_tables(cur):
    """新しいテーブル構造を作成"""

    # 1. properties（基本・取引情報）
    cur.execute(
        """
    CREATE TABLE properties (
        id SERIAL PRIMARY KEY,
        company_property_number VARCHAR(50),
        external_property_id VARCHAR(50),
        property_name VARCHAR(255) NOT NULL,
        property_name_kana VARCHAR(255),
        property_name_public BOOLEAN DEFAULT true,
        property_type property_type_enum,
        investment_property investment_property_enum DEFAULT '0:実需',
        sales_status sales_status_enum DEFAULT '1:販売中',
        publication_status publication_status_enum DEFAULT '1:公開',
        affiliated_group VARCHAR(100),
        priority_score INTEGER DEFAULT 0,
        property_url VARCHAR(500),
        
        -- 価格情報
        sale_price BIGINT,
        price_per_tsubo INTEGER,
        price_status price_status_enum DEFAULT '1:確定',
        tax_type VARCHAR(20),
        yield_rate DECIMAL(5,2),
        current_yield DECIMAL(5,2),
        management_fee INTEGER,
        repair_reserve_fund INTEGER,
        repair_reserve_fund_base INTEGER,
        parking_fee INTEGER,
        housing_insurance INTEGER,
        
        -- 契約条件
        current_status current_status_enum,
        delivery_date DATE,
        delivery_timing delivery_timing_enum,
        move_in_consultation TEXT,
        transaction_type transaction_type_enum,
        brokerage_fee INTEGER,
        commission_split_ratio DECIMAL(5,2),
        brokerage_contract_date DATE,
        listing_start_date DATE,
        listing_confirmation_date DATE,
        
        -- 元請会社情報
        contractor_company_name VARCHAR(255),
        contractor_contact_person VARCHAR(100),
        contractor_phone VARCHAR(20),
        contractor_email VARCHAR(255),
        contractor_address VARCHAR(500),
        contractor_license_number VARCHAR(50),
        
        -- 管理情報
        property_manager_name VARCHAR(100),
        internal_memo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )
    print("  ✅ properties テーブル作成完了")

    # 2. land_info（土地情報）
    cur.execute(
        """
    CREATE TABLE land_info (
        id SERIAL PRIMARY KEY,
        property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
        
        -- 所在地
        postal_code VARCHAR(10),
        address_code INTEGER,
        prefecture VARCHAR(10),
        city VARCHAR(50),
        address VARCHAR(255),
        address_detail VARCHAR(255),
        latitude DECIMAL(10, 8),
        longitude DECIMAL(11, 8),
        
        -- 土地詳細
        land_area DECIMAL(10,2),
        land_area_measurement land_area_measurement_enum,
        land_category VARCHAR(50),
        use_district use_district_enum,
        city_planning VARCHAR(100),
        building_coverage_ratio DECIMAL(5,2),
        floor_area_ratio DECIMAL(5,2),
        land_rights land_rights_enum,
        land_rent INTEGER,
        land_ownership_ratio VARCHAR(50),
        private_road_area DECIMAL(10,2),
        private_road_ratio VARCHAR(50),
        setback setback_enum,
        setback_amount DECIMAL(5,2),
        land_transaction_notice land_transaction_notice_enum,
        legal_restrictions TEXT,
        
        -- 接道状況
        road_info JSONB,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )
    print("  ✅ land_info テーブル作成完了")

    # 3. building_info（建物情報）
    cur.execute(
        """
    CREATE TABLE building_info (
        id SERIAL PRIMARY KEY,
        property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
        
        -- 建物基本情報
        building_structure building_structure_enum,
        construction_date DATE,
        building_floors_above INTEGER,
        building_floors_below INTEGER,
        total_units INTEGER,
        total_site_area DECIMAL(10,2),
        
        -- 面積情報
        building_area DECIMAL(10,2),
        total_floor_area DECIMAL(10,2),
        exclusive_area DECIMAL(10,2),
        balcony_area DECIMAL(10,2),
        area_measurement_type area_measurement_type_enum,
        
        -- 居住情報
        room_floor INTEGER,
        direction direction_enum,
        room_count INTEGER,
        room_type room_type_enum,
        floor_plans JSONB,
        floor_plan_notes TEXT,
        
        -- 管理情報（マンション）
        management_type management_type_enum,
        management_company VARCHAR(255),
        management_association management_association_enum,
        building_manager building_manager_enum,
        
        -- 駐車場
        parking_availability parking_availability_enum,
        parking_type parking_type_enum,
        parking_capacity INTEGER,
        parking_distance INTEGER,
        parking_notes TEXT,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )
    print("  ✅ building_info テーブル作成完了")

    # 4. amenities（設備・周辺環境）
    cur.execute(
        """
    CREATE TABLE amenities (
        id SERIAL PRIMARY KEY,
        property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
        
        -- 設備情報
        facilities JSONB,
        property_features TEXT,
        notes TEXT,
        
        -- 交通アクセス
        transportation JSONB,
        other_transportation VARCHAR(500),
        
        -- 周辺施設
        elementary_school_name VARCHAR(100),
        elementary_school_distance INTEGER,
        junior_high_school_name VARCHAR(100),
        junior_high_school_distance INTEGER,
        convenience_store_distance INTEGER,
        supermarket_distance INTEGER,
        general_hospital_distance INTEGER,
        shopping_street_distance INTEGER,
        drugstore_distance INTEGER,
        park_distance INTEGER,
        bank_distance INTEGER,
        other_facility_name VARCHAR(100),
        other_facility_distance INTEGER,
        
        -- リフォーム履歴
        renovations JSONB,
        
        -- エコ性能
        energy_consumption_min INTEGER,
        energy_consumption_max INTEGER,
        insulation_performance_min INTEGER,
        insulation_performance_max INTEGER,
        utility_cost_min INTEGER,
        utility_cost_max INTEGER,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )
    print("  ✅ amenities テーブル作成完了")

    # 5. property_images（画像情報）
    cur.execute(
        """
    CREATE TABLE property_images (
        id SERIAL PRIMARY KEY,
        property_id INTEGER REFERENCES properties(id) ON DELETE CASCADE,
        image_type image_type_enum,
        file_path VARCHAR(500),
        file_url VARCHAR(500),
        display_order INTEGER,
        caption TEXT,
        is_public BOOLEAN DEFAULT true,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )
    print("  ✅ property_images テーブル作成完了")

    # インデックスの作成
    print("\n📍 インデックスを作成...")
    cur.execute("CREATE INDEX idx_properties_status ON properties(sales_status)")
    cur.execute("CREATE INDEX idx_properties_type ON properties(property_type)")
    cur.execute("CREATE INDEX idx_land_info_property ON land_info(property_id)")
    cur.execute("CREATE INDEX idx_building_info_property ON building_info(property_id)")
    cur.execute("CREATE INDEX idx_amenities_property ON amenities(property_id)")
    cur.execute(
        "CREATE INDEX idx_property_images_property ON property_images(property_id)"
    )
    cur.execute(
        "CREATE INDEX idx_property_images_order ON property_images(property_id, display_order)"
    )
    print("  ✅ インデックス作成完了")


def show_new_structure(db):
    """新しいテーブル構造を表示"""
    tables = [
        "properties",
        "land_info",
        "building_info",
        "amenities",
        "property_images",
    ]

    for table in tables:
        info = db.get_table_info(table)
        print(f"\n📋 {table} ({len(info['columns'])}カラム)")
        for col in info["columns"][:5]:
            print(f"  - {col['column_name']:30s} {col['data_type']}")
        if len(info["columns"]) > 5:
            print(f"  ... 他{len(info['columns']) - 5}カラム")


if __name__ == "__main__":
    main()
