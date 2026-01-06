#!/usr/bin/env python3
"""
国土数値情報 P29（学校データ）をm_schoolsテーブルに投入するスクリプト
"""

import json
import os
import sys
import zipfile
import tempfile
import urllib.request

import psycopg2

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_connection():
    """環境変数からDB接続を取得"""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return psycopg2.connect(database_url)
    return psycopg2.connect(dbname='real_estate_db', host='localhost')

PREFECTURE_CODES = {
    '01': '北海道', '02': '青森県', '03': '岩手県', '04': '宮城県', '05': '秋田県',
    '06': '山形県', '07': '福島県', '08': '茨城県', '09': '栃木県', '10': '群馬県',
    '11': '埼玉県', '12': '千葉県', '13': '東京都', '14': '神奈川県', '15': '新潟県',
    '16': '富山県', '17': '石川県', '18': '福井県', '19': '山梨県', '20': '長野県',
    '21': '岐阜県', '22': '静岡県', '23': '愛知県', '24': '三重県', '25': '滋賀県',
    '26': '京都府', '27': '大阪府', '28': '兵庫県', '29': '奈良県', '30': '和歌山県',
    '31': '鳥取県', '32': '島根県', '33': '岡山県', '34': '広島県', '35': '山口県',
    '36': '徳島県', '37': '香川県', '38': '愛媛県', '39': '高知県', '40': '福岡県',
    '41': '佐賀県', '42': '長崎県', '43': '熊本県', '44': '大分県', '45': '宮崎県',
    '46': '鹿児島県', '47': '沖縄県'
}

ADMIN_TYPE_CODES = {'1': '国立', '2': '公立', '3': '私立'}

def download_prefecture_data(pref_code, temp_dir):
    url = f"https://nlftp.mlit.go.jp/ksj/gml/data/P29/P29-21/P29-21_{pref_code}_GML.zip"
    zip_path = os.path.join(temp_dir, f"P29-21_{pref_code}.zip")
    print(f"  ダウンロード: {url}")
    try:
        urllib.request.urlretrieve(url, zip_path)
        return zip_path
    except Exception as e:
        print(f"  エラー: {e}")
        return None

def extract_geojson(zip_path, temp_dir):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for name in zf.namelist():
            if name.endswith('.geojson'):
                zf.extract(name, temp_dir)
                return os.path.join(temp_dir, name)
    return None

def import_geojson(geojson_path, pref_code, conn):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cur = conn.cursor()
    count = 0
    
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})
        
        if geom.get('type') != 'Point':
            continue
        
        coords = geom.get('coordinates', [])
        if len(coords) < 2:
            continue
        
        lng, lat = coords[0], coords[1]
        name = str(props.get('P29_004', '') or '')
        school_type = str(props.get('P29_003', '') or '')
        admin_type_code = props.get('P29_005', '')
        address = str(props.get('P29_006', '') or '')
        admin_type_name = ADMIN_TYPE_CODES.get(str(admin_type_code), '')
        prefecture = PREFECTURE_CODES.get(pref_code, '')

        city = ''
        if address and prefecture:
            city_part = str(address).replace(prefecture, '', 1)
            for suffix in ['市', '区', '町', '村']:
                idx = city_part.find(suffix)
                if idx > 0:
                    city = city_part[:idx+1]
                    break
        
        try:
            cur.execute("""
                INSERT INTO m_schools (name, school_type, address, admin_type_name, location, prefecture_code, prefecture_name, latitude, longitude)
                VALUES (%s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s, %s, %s)
            """, (name, school_type, address, admin_type_name, lng, lat, pref_code, prefecture, lat, lng))
            count += 1
        except Exception as e:
            pass
    
    conn.commit()
    return count

def main():
    conn = get_db_connection()
    
    cur = conn.cursor()
    cur.execute("DELETE FROM m_schools")
    conn.commit()
    print("既存データクリア")
    
    total = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for pref_code, pref_name in PREFECTURE_CODES.items():
            print(f"\n{pref_name} ({pref_code})")
            
            zip_path = download_prefecture_data(pref_code, temp_dir)
            if not zip_path:
                continue
            
            geojson_path = extract_geojson(zip_path, temp_dir)
            if not geojson_path:
                print("  GeoJSONなし")
                continue
            
            count = import_geojson(geojson_path, pref_code, conn)
            print(f"  {count} 件")
            total += count
            
            os.remove(zip_path)
            os.remove(geojson_path)
    
    print(f"\n合計: {total} 件")
    
    cur.execute("SELECT school_type, COUNT(*) FROM m_schools GROUP BY school_type ORDER BY school_type")
    print("\n種別:")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    conn.close()

if __name__ == '__main__':
    main()
