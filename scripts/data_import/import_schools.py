#!/usr/bin/env python3
"""
学校データインポートスクリプト

データソース: 国土数値情報 学校データ (P29)
URL: https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-P29.html
形式: GeoJSON (P29-21_GML.zip)

対象:
- 小学校 (16001)
- 中学校 (16002)
- 中等教育学校 (16003)
- 高等学校 (16004)
- 高等専門学校 (16005)
- 短期大学 (16006)
- 大学 (16007)
- 幼稚園 (16011)
- 特別支援学校 (16012)
- 認定こども園 (16013)
- 義務教育学校 (16014)
- 各種学校 (16015)
- 専修学校 (16016)

使用方法:
    cd ~/my_programing/REA
    PYTHONPATH=~/my_programing/REA python3 scripts/data_import/import_schools.py
"""

import json
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))
from shared.database import READatabase

# ダウンロードURL
DOWNLOAD_URL = "https://nlftp.mlit.go.jp/ksj/gml/data/P29/P29-21/P29-21_GML.zip"
DATA_DIR = Path(__file__).parents[2] / "data" / "mlit_schools"
ZIP_FILE = DATA_DIR / "P29-21_GML.zip"
GEOJSON_FILE = DATA_DIR / "P29-21.geojson"

# 学校分類コードマッピング
CODE_MAPPING = {
    16001: ('elementary_school', '小学校'),
    16002: ('junior_high_school', '中学校'),
    16003: ('secondary_school', '中等教育学校'),
    16004: ('high_school', '高等学校'),
    16005: ('technical_college', '高等専門学校'),
    16006: ('junior_college', '短期大学'),
    16007: ('university', '大学'),
    16011: ('kindergarten', '幼稚園'),
    16012: ('special_needs_school', '特別支援学校'),
    16013: ('certified_childcare', '認定こども園'),
    16014: ('compulsory_school', '義務教育学校'),
    16015: ('miscellaneous_school', '各種学校'),
    16016: ('vocational_school', '専修学校'),
}

# 都道府県コード→名前
PREF_NAMES = {
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


def download_data():
    """データをダウンロード"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if GEOJSON_FILE.exists():
        print(f"既存ファイルを使用: {GEOJSON_FILE}")
        return

    print(f"ダウンロード中: {DOWNLOAD_URL}")
    urllib.request.urlretrieve(DOWNLOAD_URL, ZIP_FILE)

    print(f"解凍中: {ZIP_FILE}")
    with zipfile.ZipFile(ZIP_FILE, 'r') as z:
        z.extractall(DATA_DIR)

    print("ダウンロード完了")


def import_data():
    """データをDBにインポート"""
    with open(GEOJSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"総件数: {len(data['features'])}")

    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    # 既存データ削除
    for code, (cat_code, _) in CODE_MAPPING.items():
        cur.execute("DELETE FROM m_facilities WHERE category_code = %s AND data_source = 'MLIT'", (cat_code,))
    conn.commit()
    print("既存データ削除完了")

    # カテゴリ追加
    for code, (cat_code, cat_name) in CODE_MAPPING.items():
        cur.execute("""
            INSERT INTO m_facility_categories (category_code, category_name, icon, display_order)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (category_code) DO NOTHING
        """, (cat_code, cat_name, '🏫', 0))
    conn.commit()

    # データ投入
    inserted = 0
    for feature in data['features']:
        props = feature['properties']
        coords = feature['geometry']['coordinates']

        school_code = props['P29_003']
        if school_code not in CODE_MAPPING:
            continue

        cat_code, _ = CODE_MAPPING[school_code]
        name = props['P29_004']
        address = props['P29_005']
        pref_code = props['P29_001'][:2]
        pref_name = PREF_NAMES.get(pref_code, '')
        lon, lat = coords[0], coords[1]

        cur.execute("""
            INSERT INTO m_facilities (category_code, name, address, prefecture_code, prefecture_name,
                                      latitude, longitude, location, data_source, external_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s)
        """, (cat_code, name, address, pref_code, pref_name, lat, lon, lon, lat, 'MLIT', props['P29_002']))
        inserted += 1

        if inserted % 10000 == 0:
            print(f"{inserted}件投入...")
            conn.commit()

    conn.commit()
    print(f"完了: {inserted}件投入")

    # データソーステーブル更新
    cur.execute("""
        UPDATE m_data_sources
        SET last_updated = CURRENT_DATE, updated_at = CURRENT_TIMESTAMP
        WHERE source_name = '国土数値情報 学校データ'
    """)
    conn.commit()

    cur.close()
    conn.close()


if __name__ == '__main__':
    download_data()
    import_data()
