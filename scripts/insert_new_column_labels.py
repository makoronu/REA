#!/usr/bin/env python3
"""
新しいテーブル構造用の日本語ラベル登録スクリプト
"""

import sys
sys.path.append('.')
from shared.database import READatabase
from datetime import datetime

def main():
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()
    
    try:
        print("🚀 日本語ラベル登録開始...")
        
        # 各テーブルのラベルを定義
        table_labels = {
            'properties': create_properties_labels(),
            'land_info': create_land_info_labels(),
            'building_info': create_building_info_labels(),
            'amenities': create_amenities_labels(),
            'property_images': create_property_images_labels()
        }
        
        total_inserted = 0
        
        for table_name, labels in table_labels.items():
            print(f"\n📋 {table_name} のラベルを登録中...")
            
            for idx, label_data in enumerate(labels, 1):
                insert_query = """
                INSERT INTO column_labels (
                    table_name, column_name, japanese_label, description,
                    display_order, group_name, data_type, enum_values,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cur.execute(insert_query, (
                    table_name,
                    label_data['column_name'],
                    label_data['japanese_label'],
                    label_data.get('description', ''),
                    idx,
                    label_data.get('group_name', ''),
                    label_data.get('data_type', ''),
                    label_data.get('enum_values', ''),
                    datetime.now(),
                    datetime.now()
                ))
                
            print(f"  ✅ {len(labels)}件のラベルを登録")
            total_inserted += len(labels)
        
        conn.commit()
        print(f"\n✅ 合計 {total_inserted} 件のラベルを登録完了！")
        
        # 登録結果を確認
        print("\n📊 登録結果:")
        for table in table_labels.keys():
            cur.execute("SELECT COUNT(*) FROM column_labels WHERE table_name = %s", (table,))
            count = cur.fetchone()[0]
            print(f"  {table:20s}: {count}件")
            
    except Exception as e:
        conn.rollback()
        print(f"\n❌ エラー: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def create_properties_labels():
    """propertiesテーブルのラベル定義"""
    return [
        # システムカラム（非表示）
        {'column_name': 'id', 'japanese_label': 'ID', 'group_name': 'システム', 'description': 'プライマリキー'},
        
        # 基本情報
        {'column_name': 'company_property_number', 'japanese_label': '自社物件番号', 'group_name': '基本情報', 'description': '社内管理番号'},
        {'column_name': 'external_property_id', 'japanese_label': '外部連携ID', 'group_name': '基本情報', 'description': '外部システムID'},
        {'column_name': 'property_name', 'japanese_label': '物件名', 'group_name': '基本情報', 'description': '物件の正式名称'},
        {'column_name': 'property_name_kana', 'japanese_label': '物件名カナ', 'group_name': '基本情報', 'description': 'カナ表記'},
        {'column_name': 'property_name_public', 'japanese_label': '物件名公開', 'group_name': '基本情報', 'description': '物件名を公開するか', 'data_type': 'boolean'},
        {'column_name': 'property_type', 'japanese_label': '物件種別', 'group_name': '基本情報', 'enum_values': '1:マンション,2:一戸建て,3:土地,4:その他'},
        {'column_name': 'investment_property', 'japanese_label': '投資物件', 'group_name': '基本情報', 'enum_values': '0:実需,1:投資'},
        {'column_name': 'sales_status', 'japanese_label': '販売状況', 'group_name': '基本情報', 'enum_values': '1:販売中,2:商談中,3:成約済み,4:販売終了'},
        {'column_name': 'publication_status', 'japanese_label': '公開状態', 'group_name': '基本情報', 'enum_values': '1:公開,2:非公開,3:限定公開'},
        {'column_name': 'affiliated_group', 'japanese_label': '所属グループ', 'group_name': '基本情報', 'description': '支店・グループ名'},
        {'column_name': 'priority_score', 'japanese_label': '優先度スコア', 'group_name': '基本情報', 'description': '表示優先度'},
        {'column_name': 'property_url', 'japanese_label': '物件詳細URL', 'group_name': '基本情報', 'description': '物件詳細ページのURL'},
        
        # 価格情報
        {'column_name': 'sale_price', 'japanese_label': '売買価格', 'group_name': '価格情報', 'description': '販売価格（円）'},
        {'column_name': 'price_per_tsubo', 'japanese_label': '坪単価', 'group_name': '価格情報', 'description': '1坪あたりの価格'},
        {'column_name': 'price_status', 'japanese_label': '価格状態', 'group_name': '価格情報', 'enum_values': '1:確定,2:相談,3:応相談'},
        {'column_name': 'tax_type', 'japanese_label': '税込/税抜', 'group_name': '価格情報', 'description': '価格の税表示'},
        {'column_name': 'yield_rate', 'japanese_label': '表面利回り', 'group_name': '価格情報', 'description': '投資物件の利回り(%)'},
        {'column_name': 'current_yield', 'japanese_label': '現行利回り', 'group_name': '価格情報', 'description': '現在の利回り(%)'},
        {'column_name': 'management_fee', 'japanese_label': '管理費', 'group_name': '価格情報', 'description': 'マンションの管理費'},
        {'column_name': 'repair_reserve_fund', 'japanese_label': '修繕積立金', 'group_name': '価格情報', 'description': 'マンションの修繕積立金'},
        {'column_name': 'repair_reserve_fund_base', 'japanese_label': '修繕積立基金', 'group_name': '価格情報', 'description': '一時金'},
        {'column_name': 'parking_fee', 'japanese_label': '駐車場使用料', 'group_name': '価格情報', 'description': '月額駐車場代'},
        {'column_name': 'housing_insurance', 'japanese_label': '住宅保険料', 'group_name': '価格情報', 'description': '年間保険料'},
        
        # 契約条件
        {'column_name': 'current_status', 'japanese_label': '現況', 'group_name': '契約条件', 'enum_values': '1:空家,2:居住中,3:賃貸中,9:その他'},
        {'column_name': 'delivery_date', 'japanese_label': '引渡予定日', 'group_name': '契約条件', 'description': '引渡し予定日', 'data_type': 'date'},
        {'column_name': 'delivery_timing', 'japanese_label': '引渡時期', 'group_name': '契約条件', 'enum_values': '1:即時,2:相談,3:期日指定'},
        {'column_name': 'move_in_consultation', 'japanese_label': '引渡時期相談内容', 'group_name': '契約条件', 'description': '相談内容の詳細'},
        {'column_name': 'transaction_type', 'japanese_label': '取引態様', 'group_name': '契約条件', 'enum_values': '1:売主,2:代理,3:専任媒介,4:一般媒介,5:専属専任'},
        {'column_name': 'brokerage_fee', 'japanese_label': '仲介手数料', 'group_name': '契約条件', 'description': '仲介手数料（円）'},
        {'column_name': 'commission_split_ratio', 'japanese_label': '分配率（客付分）', 'group_name': '契約条件', 'description': '業者間の手数料分配率(%)'},
        {'column_name': 'brokerage_contract_date', 'japanese_label': '媒介契約日', 'group_name': '契約条件', 'description': '媒介契約締結日', 'data_type': 'date'},
        {'column_name': 'listing_start_date', 'japanese_label': '掲載開始日', 'group_name': '契約条件', 'description': '広告掲載開始日', 'data_type': 'date'},
        {'column_name': 'listing_confirmation_date', 'japanese_label': '掲載確認日', 'group_name': '契約条件', 'description': '最終確認日', 'data_type': 'date'},
        
        # 元請会社情報
        {'column_name': 'contractor_company_name', 'japanese_label': '元請会社名', 'group_name': '元請会社', 'description': '元請会社の正式名称'},
        {'column_name': 'contractor_contact_person', 'japanese_label': '担当者名', 'group_name': '元請会社', 'description': '元請会社の担当者'},
        {'column_name': 'contractor_phone', 'japanese_label': '電話番号', 'group_name': '元請会社', 'description': '元請会社の電話番号'},
        {'column_name': 'contractor_email', 'japanese_label': 'メールアドレス', 'group_name': '元請会社', 'description': '元請会社のメール'},
        {'column_name': 'contractor_address', 'japanese_label': '会社住所', 'group_name': '元請会社', 'description': '元請会社の所在地'},
        {'column_name': 'contractor_license_number', 'japanese_label': '宅建免許番号', 'group_name': '元請会社', 'description': '宅地建物取引業免許番号'},
        
        # 管理情報
        {'column_name': 'property_manager_name', 'japanese_label': '社内担当者', 'group_name': '管理情報', 'description': '社内の物件担当者'},
        {'column_name': 'internal_memo', 'japanese_label': '社内メモ', 'group_name': '管理情報', 'description': '社内用の備考'},
        {'column_name': 'created_at', 'japanese_label': '作成日時', 'group_name': 'システム', 'description': 'レコード作成日時'},
        {'column_name': 'updated_at', 'japanese_label': '更新日時', 'group_name': 'システム', 'description': 'レコード更新日時'}
    ]

def create_land_info_labels():
    """land_infoテーブルのラベル定義"""
    return [
        {'column_name': 'id', 'japanese_label': 'ID', 'group_name': 'システム', 'description': 'プライマリキー'},
        {'column_name': 'property_id', 'japanese_label': '物件ID', 'group_name': 'システム', 'description': '物件への外部キー'},
        
        # 所在地
        {'column_name': 'postal_code', 'japanese_label': '郵便番号', 'group_name': '所在地', 'description': '郵便番号（ハイフン付き）'},
        {'column_name': 'address_code', 'japanese_label': '所在地コード', 'group_name': '所在地', 'description': '住所コード'},
        {'column_name': 'prefecture', 'japanese_label': '都道府県', 'group_name': '所在地', 'description': '都道府県名'},
        {'column_name': 'city', 'japanese_label': '市区町村', 'group_name': '所在地', 'description': '市区町村名'},
        {'column_name': 'address', 'japanese_label': '町名番地', 'group_name': '所在地', 'description': '町名・番地'},
        {'column_name': 'address_detail', 'japanese_label': '建物名・部屋番号', 'group_name': '所在地', 'description': '建物名・部屋番号（非公開）'},
        {'column_name': 'latitude', 'japanese_label': '緯度', 'group_name': '所在地', 'description': '緯度情報'},
        {'column_name': 'longitude', 'japanese_label': '経度', 'group_name': '所在地', 'description': '経度情報'},
        
        # 土地詳細
        {'column_name': 'land_area', 'japanese_label': '土地面積', 'group_name': '土地詳細', 'description': '土地面積（㎡）'},
        {'column_name': 'land_area_measurement', 'japanese_label': '計測方式', 'group_name': '土地詳細', 'enum_values': '1:公簿,2:実測,3:私測'},
        {'column_name': 'land_category', 'japanese_label': '地目', 'group_name': '土地詳細', 'description': '土地の地目'},
        {'column_name': 'use_district', 'japanese_label': '用途地域', 'group_name': '土地詳細', 'enum_values': '1:第一種低層住居専用,2:第二種低層住居専用,3:第一種中高層住居専用,4:第二種中高層住居専用,5:第一種住居,6:第二種住居,7:準住居,8:近隣商業,9:商業,10:準工業,11:工業,12:工業専用'},
        {'column_name': 'city_planning', 'japanese_label': '都市計画', 'group_name': '土地詳細', 'description': '都市計画区域'},
        {'column_name': 'building_coverage_ratio', 'japanese_label': '建ぺい率', 'group_name': '土地詳細', 'description': '建ぺい率（%）'},
        {'column_name': 'floor_area_ratio', 'japanese_label': '容積率', 'group_name': '土地詳細', 'description': '容積率（%）'},
        {'column_name': 'land_rights', 'japanese_label': '土地権利', 'group_name': '土地詳細', 'enum_values': '1:所有権,2:借地権,3:定期借地権,4:地上権'},
        {'column_name': 'land_rent', 'japanese_label': '借地料', 'group_name': '土地詳細', 'description': '借地料（円/月）'},
        {'column_name': 'land_ownership_ratio', 'japanese_label': '土地持分', 'group_name': '土地詳細', 'description': '土地の共有持分'},
        {'column_name': 'private_road_area', 'japanese_label': '私道負担面積', 'group_name': '土地詳細', 'description': '私道負担面積（㎡）'},
        {'column_name': 'private_road_ratio', 'japanese_label': '私道負担割合', 'group_name': '土地詳細', 'description': '私道の共有持分'},
        {'column_name': 'setback', 'japanese_label': 'セットバック', 'group_name': '土地詳細', 'enum_values': '0:不要,1:要,2:セットバック済'},
        {'column_name': 'setback_amount', 'japanese_label': 'セットバック量', 'group_name': '土地詳細', 'description': 'セットバック面積（㎡）'},
        {'column_name': 'land_transaction_notice', 'japanese_label': '国土法届出', 'group_name': '土地詳細', 'enum_values': '0:不要,1:要,2:届出済'},
        {'column_name': 'legal_restrictions', 'japanese_label': '法令上の制限', 'group_name': '土地詳細', 'description': 'その他法令制限'},
        
        # 接道状況
        {'column_name': 'road_info', 'japanese_label': '接道情報', 'group_name': '接道', 'description': '接道の詳細情報（JSON）', 'data_type': 'jsonb'},
        
        {'column_name': 'created_at', 'japanese_label': '作成日時', 'group_name': 'システム', 'description': 'レコード作成日時'},
        {'column_name': 'updated_at', 'japanese_label': '更新日時', 'group_name': 'システム', 'description': 'レコード更新日時'}
    ]

def create_building_info_labels():
    """building_infoテーブルのラベル定義"""
    return [
        {'column_name': 'id', 'japanese_label': 'ID', 'group_name': 'システム', 'description': 'プライマリキー'},
        {'column_name': 'property_id', 'japanese_label': '物件ID', 'group_name': 'システム', 'description': '物件への外部キー'},
        
        # 建物基本情報
        {'column_name': 'building_structure', 'japanese_label': '建物構造', 'group_name': '建物基本', 'enum_values': '1:木造,2:鉄骨造,3:RC造,4:SRC造,5:軽量鉄骨,6:ALC,9:その他'},
        {'column_name': 'construction_date', 'japanese_label': '築年月', 'group_name': '建物基本', 'description': '建築年月', 'data_type': 'date'},
        {'column_name': 'building_floors_above', 'japanese_label': '地上階数', 'group_name': '建物基本', 'description': '地上階数'},
        {'column_name': 'building_floors_below', 'japanese_label': '地下階数', 'group_name': '建物基本', 'description': '地下階数'},
        {'column_name': 'total_units', 'japanese_label': '総戸数', 'group_name': '建物基本', 'description': 'マンションの総戸数'},
        {'column_name': 'total_site_area', 'japanese_label': '敷地全体面積', 'group_name': '建物基本', 'description': '敷地全体の面積（㎡）'},
        
        # 面積情報
        {'column_name': 'building_area', 'japanese_label': '建築面積', 'group_name': '面積', 'description': '建築面積（㎡）'},
        {'column_name': 'total_floor_area', 'japanese_label': '延床面積', 'group_name': '面積', 'description': '延床面積（㎡）'},
        {'column_name': 'exclusive_area', 'japanese_label': '専有面積', 'group_name': '面積', 'description': '専有面積（㎡）'},
        {'column_name': 'balcony_area', 'japanese_label': 'バルコニー面積', 'group_name': '面積', 'description': 'バルコニー面積（㎡）'},
        {'column_name': 'area_measurement_type', 'japanese_label': '面積計測方式', 'group_name': '面積', 'enum_values': '1:壁芯,2:内法,3:登記簿'},
        
        # 居住情報
        {'column_name': 'room_floor', 'japanese_label': '所在階', 'group_name': '居住情報', 'description': '部屋の所在階'},
        {'column_name': 'direction', 'japanese_label': '向き', 'group_name': '居住情報', 'enum_values': '1:北,2:北東,3:東,4:南東,5:南,6:南西,7:西,8:北西'},
        {'column_name': 'room_count', 'japanese_label': '間取り部屋数', 'group_name': '居住情報', 'description': '部屋数'},
        {'column_name': 'room_type', 'japanese_label': '間取りタイプ', 'group_name': '居住情報', 'enum_values': '1:R,2:K,3:DK,4:LDK,5:SLDK,6:その他'},
        {'column_name': 'floor_plans', 'japanese_label': '間取り詳細', 'group_name': '居住情報', 'description': '間取りの詳細情報（JSON）', 'data_type': 'jsonb'},
        {'column_name': 'floor_plan_notes', 'japanese_label': '間取り備考', 'group_name': '居住情報', 'description': '間取りの補足説明'},
        
        # 管理情報
        {'column_name': 'management_type', 'japanese_label': '管理形態', 'group_name': '管理情報', 'enum_values': '1:自主管理,2:管理会社委託,3:一部委託,9:その他'},
        {'column_name': 'management_company', 'japanese_label': '管理会社名', 'group_name': '管理情報', 'description': '管理会社の名称'},
        {'column_name': 'management_association', 'japanese_label': '管理組合', 'group_name': '管理情報', 'enum_values': '0:無,1:有'},
        {'column_name': 'building_manager', 'japanese_label': '管理人', 'group_name': '管理情報', 'enum_values': '1:常駐,2:日勤,3:巡回,4:自主管理,9:無'},
        
        # 駐車場
        {'column_name': 'parking_availability', 'japanese_label': '駐車場', 'group_name': '駐車場', 'enum_values': '1:無,2:有(無料),3:有(有料),4:近隣(無料),5:近隣(有料)'},
        {'column_name': 'parking_type', 'japanese_label': '駐車場種別', 'group_name': '駐車場', 'enum_values': '1:平置き,2:機械式,3:立体,9:その他'},
        {'column_name': 'parking_capacity', 'japanese_label': '駐車可能台数', 'group_name': '駐車場', 'description': '駐車可能台数'},
        {'column_name': 'parking_distance', 'japanese_label': '駐車場距離', 'group_name': '駐車場', 'description': '駐車場までの距離（m）'},
        {'column_name': 'parking_notes', 'japanese_label': '駐車場備考', 'group_name': '駐車場', 'description': '駐車場の補足情報'},
        
        {'column_name': 'created_at', 'japanese_label': '作成日時', 'group_name': 'システム', 'description': 'レコード作成日時'},
        {'column_name': 'updated_at', 'japanese_label': '更新日時', 'group_name': 'システム', 'description': 'レコード更新日時'}
    ]

def create_amenities_labels():
    """amenitiesテーブルのラベル定義"""
    return [
        {'column_name': 'id', 'japanese_label': 'ID', 'group_name': 'システム', 'description': 'プライマリキー'},
        {'column_name': 'property_id', 'japanese_label': '物件ID', 'group_name': 'システム', 'description': '物件への外部キー'},
        
        # 設備情報
        {'column_name': 'facilities', 'japanese_label': '設備', 'group_name': '設備', 'description': '設備一覧（JSON配列）', 'data_type': 'jsonb'},
        {'column_name': 'property_features', 'japanese_label': '物件の特徴', 'group_name': '設備', 'description': 'セールスポイント'},
        {'column_name': 'notes', 'japanese_label': 'その他特記事項', 'group_name': '設備', 'description': '補足説明'},
        
        # 交通アクセス
        {'column_name': 'transportation', 'japanese_label': '交通情報', 'group_name': '交通', 'description': '最寄り駅情報（JSON）', 'data_type': 'jsonb'},
        {'column_name': 'other_transportation', 'japanese_label': 'その他交通', 'group_name': '交通', 'description': 'その他の交通手段'},
        
        # 周辺施設
        {'column_name': 'elementary_school_name', 'japanese_label': '小学校名', 'group_name': '周辺施設', 'description': '学区の小学校名'},
        {'column_name': 'elementary_school_distance', 'japanese_label': '小学校距離', 'group_name': '周辺施設', 'description': '小学校までの距離（m）'},
        {'column_name': 'junior_high_school_name', 'japanese_label': '中学校名', 'group_name': '周辺施設', 'description': '学区の中学校名'},
        {'column_name': 'junior_high_school_distance', 'japanese_label': '中学校距離', 'group_name': '周辺施設', 'description': '中学校までの距離（m）'},
        {'column_name': 'convenience_store_distance', 'japanese_label': 'コンビニ距離', 'group_name': '周辺施設', 'description': '最寄りコンビニまでの距離（m）'},
        {'column_name': 'supermarket_distance', 'japanese_label': 'スーパー距離', 'group_name': '周辺施設', 'description': '最寄りスーパーまでの距離（m）'},
        {'column_name': 'general_hospital_distance', 'japanese_label': '総合病院距離', 'group_name': '周辺施設', 'description': '総合病院までの距離（m）'},
        {'column_name': 'shopping_street_distance', 'japanese_label': '商店街距離', 'group_name': '周辺施設', 'description': '商店街までの距離（m）'},
        {'column_name': 'drugstore_distance', 'japanese_label': 'ドラッグストア距離', 'group_name': '周辺施設', 'description': 'ドラッグストアまでの距離（m）'},
        {'column_name': 'park_distance', 'japanese_label': '公園距離', 'group_name': '周辺施設', 'description': '最寄り公園までの距離（m）'},
        {'column_name': 'bank_distance', 'japanese_label': '銀行距離', 'group_name': '周辺施設', 'description': '最寄り銀行までの距離（m）'},
        {'column_name': 'other_facility_name', 'japanese_label': 'その他施設名', 'group_name': '周辺施設', 'description': 'その他の重要施設'},
        {'column_name': 'other_facility_distance', 'japanese_label': 'その他施設距離', 'group_name': '周辺施設', 'description': 'その他施設までの距離（m）'},
        
        # リフォーム履歴
        {'column_name': 'renovations', 'japanese_label': 'リフォーム履歴', 'group_name': 'リフォーム', 'description': 'リフォーム履歴（JSON）', 'data_type': 'jsonb'},
        
        # エコ性能
        {'column_name': 'energy_consumption_min', 'japanese_label': 'エネルギー消費性能(最小)', 'group_name': 'エコ性能', 'description': '省エネ性能の下限値'},
        {'column_name': 'energy_consumption_max', 'japanese_label': 'エネルギー消費性能(最大)', 'group_name': 'エコ性能', 'description': '省エネ性能の上限値'},
        {'column_name': 'insulation_performance_min', 'japanese_label': '断熱性能(最小)', 'group_name': 'エコ性能', 'description': '断熱性能の下限値'},
        {'column_name': 'insulation_performance_max', 'japanese_label': '断熱性能(最大)', 'group_name': 'エコ性能', 'description': '断熱性能の上限値'},
        {'column_name': 'utility_cost_min', 'japanese_label': '目安光熱費(最小)', 'group_name': 'エコ性能', 'description': '月額光熱費の下限（円）'},
        {'column_name': 'utility_cost_max', 'japanese_label': '目安光熱費(最大)', 'group_name': 'エコ性能', 'description': '月額光熱費の上限（円）'},
        
        {'column_name': 'created_at', 'japanese_label': '作成日時', 'group_name': 'システム', 'description': 'レコード作成日時'},
        {'column_name': 'updated_at', 'japanese_label': '更新日時', 'group_name': 'システム', 'description': 'レコード更新日時'}
    ]

def create_property_images_labels():
    """property_imagesテーブルのラベル定義"""
    return [
        {'column_name': 'id', 'japanese_label': 'ID', 'group_name': 'システム', 'description': 'プライマリキー'},
        {'column_name': 'property_id', 'japanese_label': '物件ID', 'group_name': 'システム', 'description': '物件への外部キー'},
        {'column_name': 'image_type', 'japanese_label': '画像種別', 'group_name': '画像情報', 'enum_values': '01:外観,02:間取図,03:居室,04:キッチン,05:風呂,06:トイレ,07:洗面,08:設備,09:玄関,10:バルコニー,11:眺望,12:共用部,13:周辺環境,14:その他'},
        {'column_name': 'file_path', 'japanese_label': 'ファイルパス', 'group_name': '画像情報', 'description': 'ローカルファイルパス'},
        {'column_name': 'file_url', 'japanese_label': '公開URL', 'group_name': '画像情報', 'description': '画像の公開URL'},
        {'column_name': 'display_order', 'japanese_label': '表示順', 'group_name': '画像情報', 'description': '表示順序'},
        {'column_name': 'caption', 'japanese_label': 'キャプション', 'group_name': '画像情報', 'description': '画像の説明文'},
        {'column_name': 'is_public', 'japanese_label': '公開フラグ', 'group_name': '画像情報', 'description': '画像を公開するか', 'data_type': 'boolean'},
        {'column_name': 'uploaded_at', 'japanese_label': 'アップロード日時', 'group_name': '画像情報', 'description': '画像のアップロード日時'},
        {'column_name': 'created_at', 'japanese_label': '作成日時', 'group_name': 'システム', 'description': 'レコード作成日時'},
        {'column_name': 'updated_at', 'japanese_label': '更新日時', 'group_name': 'システム', 'description': 'レコード更新日時'}
    ]

if __name__ == "__main__":
    main()