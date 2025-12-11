#!/usr/bin/env python3
"""
国土数値情報から学校データをダウンロード・インポート
- P29: 学校データ（小学校・中学校・高等学校等の位置）
"""
import os
import sys
import json
import zipfile
import tempfile
import urllib.request
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database import READatabase

# データ保存先
DATA_DIR = Path(__file__).parent.parent / "data" / "schools"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 都道府県コード
PREFECTURES = {
    "01": "北海道", "02": "青森県", "03": "岩手県", "04": "宮城県", "05": "秋田県",
    "06": "山形県", "07": "福島県", "08": "茨城県", "09": "栃木県", "10": "群馬県",
    "11": "埼玉県", "12": "千葉県", "13": "東京都", "14": "神奈川県", "15": "新潟県",
    "16": "富山県", "17": "石川県", "18": "福井県", "19": "山梨県", "20": "長野県",
    "21": "岐阜県", "22": "静岡県", "23": "愛知県", "24": "三重県", "25": "滋賀県",
    "26": "京都府", "27": "大阪府", "28": "兵庫県", "29": "奈良県", "30": "和歌山県",
    "31": "鳥取県", "32": "島根県", "33": "岡山県", "34": "広島県", "35": "山口県",
    "36": "徳島県", "37": "香川県", "38": "愛媛県", "39": "高知県", "40": "福岡県",
    "41": "佐賀県", "42": "長崎県", "43": "熊本県", "44": "大分県", "45": "宮崎県",
    "46": "鹿児島県", "47": "沖縄県"
}

# 学校分類コード（整数型）
SCHOOL_TYPES = {
    16001: "小学校",
    16002: "中学校",
    16003: "義務教育学校",
    16004: "高等学校",
    16005: "中等教育学校",
    16006: "特別支援学校",
    16007: "高等専門学校",
    16008: "短期大学",
    16009: "大学",
    16011: "幼稚園",
    16012: "幼保連携型認定こども園",
    16013: "専修学校",
    16014: "各種学校",
    16015: "その他の教育施設",
    16016: "保育所等"
}

# 管理者コード（整数型）
ADMIN_TYPES = {
    1: "国立",
    2: "公立",
    3: "私立",
    4: "私立"  # 4も私立として扱う
}


def create_schools_table(cur):
    """学校テーブル作成"""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS m_schools (
            id SERIAL PRIMARY KEY,
            school_code VARCHAR(20) UNIQUE,
            school_type VARCHAR(20) NOT NULL,
            school_type_name VARCHAR(50),
            name VARCHAR(200) NOT NULL,
            address VARCHAR(500),
            prefecture_code VARCHAR(2),
            prefecture_name VARCHAR(20),
            admin_type VARCHAR(10),
            admin_type_name VARCHAR(20),
            is_closed BOOLEAN DEFAULT FALSE,
            latitude DECIMAL(10, 7),
            longitude DECIMAL(10, 7),
            location GEOMETRY(Point, 4326),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # インデックス作成
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_m_schools_location
        ON m_schools USING GIST (location)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_m_schools_type
        ON m_schools (school_type)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_m_schools_prefecture
        ON m_schools (prefecture_code)
    """)
    print("✅ m_schools テーブル作成完了")


def download_school_data(pref_code: str) -> Path:
    """都道府県別の学校データをダウンロード"""
    # 令和3年度データ (P29-21)
    url = f"https://nlftp.mlit.go.jp/ksj/gml/data/P29/P29-21/P29-21_{pref_code}_GML.zip"
    zip_path = DATA_DIR / f"P29-21_{pref_code}_GML.zip"

    if zip_path.exists():
        print(f"  キャッシュ使用: {zip_path.name}")
        return zip_path

    print(f"  ダウンロード中: {url}")
    try:
        urllib.request.urlretrieve(url, zip_path)
        return zip_path
    except Exception as e:
        print(f"  ❌ ダウンロード失敗: {e}")
        return None


def parse_geojson(geojson_path: Path) -> list:
    """GeoJSONファイルをパース"""
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    schools = []
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})

        if geom.get('type') != 'Point':
            continue

        coords = geom.get('coordinates', [])
        if len(coords) < 2:
            continue

        school = {
            'school_code': str(props.get('P29_002', '')),
            'school_type': props.get('P29_003'),  # 整数型のまま
            'name': props.get('P29_004', ''),
            'address': props.get('P29_005', ''),
            'admin_code': props.get('P29_006'),  # 整数型のまま
            'is_closed': props.get('P29_007', 1) == 2,  # 2=休校
            'longitude': coords[0],
            'latitude': coords[1]
        }
        schools.append(school)

    return schools


def parse_shapefile(shp_dir: Path) -> list:
    """Shapefileをパース（pyshp使用）"""
    try:
        import shapefile
    except ImportError:
        print("  pyshp未インストール。pip install pyshp を実行してください")
        return []

    # P29ファイルを探す
    shp_files = list(shp_dir.glob("**/P29*.shp"))
    if not shp_files:
        return []

    schools = []
    for shp_file in shp_files:
        sf = shapefile.Reader(str(shp_file), encoding='cp932')

        # フィールド名を取得
        fields = [f[0] for f in sf.fields[1:]]

        for sr in sf.shapeRecords():
            props = dict(zip(fields, sr.record))

            if sr.shape.shapeType != 1:  # Point
                continue

            school = {
                'school_code': str(props.get('P29_002', '')),
                'school_type': str(props.get('P29_003', '')),
                'name': str(props.get('P29_004', '')),
                'address': str(props.get('P29_005', '')),
                'admin_code': str(props.get('P29_006', '')),
                'is_closed': str(props.get('P29_007', '0')) == '1',
                'longitude': sr.shape.points[0][0],
                'latitude': sr.shape.points[0][1]
            }
            schools.append(school)

    return schools


def extract_and_parse(zip_path: Path, pref_code: str) -> list:
    """ZIPを展開してパース"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)

        tmppath = Path(tmpdir)

        # GeoJSONを優先的に探す
        geojson_files = list(tmppath.glob("**/*.geojson"))
        if geojson_files:
            return parse_geojson(geojson_files[0])

        # Shapefileを探す
        return parse_shapefile(tmppath)


def insert_schools(cur, schools: list, pref_code: str):
    """学校データをDBに挿入"""
    pref_name = PREFECTURES.get(pref_code, '')

    for school in schools:
        school_type = school['school_type']
        school_type_name = SCHOOL_TYPES.get(school_type, '')
        admin_type_name = ADMIN_TYPES.get(school['admin_code'], '')

        # 小学校・中学校・義務教育学校のみ（必要に応じて変更）
        if school_type not in [16001, 16002, 16003]:
            continue

        try:
            cur.execute("""
                INSERT INTO m_schools (
                    school_code, school_type, school_type_name, name, address,
                    prefecture_code, prefecture_name, admin_type, admin_type_name,
                    is_closed, latitude, longitude, location
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                )
                ON CONFLICT (school_code) DO UPDATE SET
                    name = EXCLUDED.name,
                    address = EXCLUDED.address,
                    is_closed = EXCLUDED.is_closed,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    location = EXCLUDED.location
            """, (
                school['school_code'], school_type, school_type_name, school['name'], school['address'],
                pref_code, pref_name, school['admin_code'], admin_type_name,
                school['is_closed'], school['latitude'], school['longitude'],
                school['longitude'], school['latitude']
            ))
        except Exception as e:
            print(f"    挿入エラー: {school['name']} - {e}")


def main():
    print("=" * 60)
    print("国土数値情報 学校データインポート")
    print("=" * 60)

    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # テーブル作成
        create_schools_table(cur)
        conn.commit()

        total_count = 0

        # 全都道府県を処理
        for pref_code, pref_name in PREFECTURES.items():
            print(f"\n📍 {pref_name}({pref_code})...")

            # ダウンロード
            zip_path = download_school_data(pref_code)
            if not zip_path:
                continue

            # パース
            schools = extract_and_parse(zip_path, pref_code)
            print(f"  学校数: {len(schools)}")

            # 挿入
            insert_schools(cur, schools, pref_code)
            conn.commit()

            total_count += len([s for s in schools if s['school_type'] in ['16001', '16002', '16003']])

        # 最終確認
        cur.execute("SELECT COUNT(*) FROM m_schools")
        db_count = cur.fetchone()[0]

        cur.execute("""
            SELECT school_type_name, COUNT(*)
            FROM m_schools
            GROUP BY school_type_name
            ORDER BY school_type_name
        """)
        type_counts = cur.fetchall()

        print("\n" + "=" * 60)
        print(f"✅ インポート完了: {db_count}校")
        for type_name, count in type_counts:
            print(f"   - {type_name}: {count}校")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        print(f"❌ エラー: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
