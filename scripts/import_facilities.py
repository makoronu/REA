#!/usr/bin/env python3
"""
国土数値情報から施設データをダウンロード・インポート
- P04: 医療機関データ
- P13: 都市公園データ
- P14: 福祉施設データ
- P27: 文化施設データ
- P30: 郵便局データ
"""
import os
import sys
import json
import zipfile
import tempfile
import urllib.request
from pathlib import Path
import shapefile  # pyshp

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database import READatabase

# データ保存先
DATA_DIR = Path(__file__).parent.parent / "data" / "facilities"
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


def download_data(data_type: str, pref_code: str) -> Path:
    """データをダウンロード"""
    # データタイプ別のURL設定
    url_patterns = {
        'P04': ('P04-20', 'https://nlftp.mlit.go.jp/ksj/gml/data/P04/P04-20/P04-20_{}_GML.zip'),  # 医療機関
        'P13': ('P13-11', 'https://nlftp.mlit.go.jp/ksj/gml/data/P13/P13-11/P13-11_{}_GML.zip'),  # 都市公園
        'P14': ('P14-15', 'https://nlftp.mlit.go.jp/ksj/gml/data/P14/P14-15/P14-15_{}_GML.zip'),  # 福祉施設
        'P27': ('P27-13', 'https://nlftp.mlit.go.jp/ksj/gml/data/P27/P27-13/P27-13_{}.zip'),  # 文化施設
        'P30': ('P30-13', 'https://nlftp.mlit.go.jp/ksj/gml/data/P30/P30-13/P30-13_{}.zip'),  # 郵便局（GMLなし）
    }

    if data_type not in url_patterns:
        print(f"  ❌ 不明なデータタイプ: {data_type}")
        return None

    prefix, url_template = url_patterns[data_type]
    url = url_template.format(pref_code)
    zip_path = DATA_DIR / f"{prefix}_{pref_code}_GML.zip"

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


def parse_medical_geojson(geojson_path: Path) -> list:
    """医療機関GeoJSONをパース (P04)"""
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    facilities = []

    for feature in data.get('features', []):
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})

        if geom.get('type') != 'Point':
            continue

        coords = geom.get('coordinates', [])
        if len(coords) < 2:
            continue

        # P04_001: 医療機関分類（1:病院, 2:一般診療所, 3:歯科診療所）
        med_type = str(props.get('P04_001', ''))
        # P04_002: 施設名
        name = props.get('P04_002', '') or ''
        # P04_003: 住所
        address = props.get('P04_003', '') or ''

        # カテゴリ決定（病院 or 診療所）
        category = 'hospital' if med_type == '1' else 'clinic'

        facilities.append({
            'name': name,
            'address': address,
            'category_code': category,
            'latitude': coords[1],
            'longitude': coords[0],
            'metadata': {'type_code': med_type}
        })

    return facilities


def parse_park_shapefile(shp_path: Path) -> list:
    """都市公園Shapefileをパース (P13)"""
    facilities = []

    sf = shapefile.Reader(str(shp_path), encoding='cp932')
    fields = [f[0] for f in sf.fields[1:]]  # 最初はDeletionFlag

    for sr in sf.shapeRecords():
        shape = sr.shape
        record = dict(zip(fields, sr.record))

        # ポイントでない場合はスキップ
        if shape.shapeType != shapefile.POINT:
            continue

        coords = shape.points[0] if shape.points else None
        if not coords:
            continue

        # P13_003: 公園名
        name = record.get('P13_003', '') or ''
        # P13_005: 都道府県名, P13_006: 市区町村名
        pref = record.get('P13_005', '') or ''
        city = record.get('P13_006', '') or ''
        address = '{}{}'.format(pref, city)

        facilities.append({
            'name': name,
            'address': address,
            'category_code': 'park',
            'latitude': coords[1],  # shapefile: (lon, lat)
            'longitude': coords[0],
            'metadata': {}
        })

    return facilities


def parse_post_office_shapefile(shp_path: Path) -> list:
    """郵便局Shapefileをパース (P30)"""
    facilities = []

    sf = shapefile.Reader(str(shp_path), encoding='cp932')
    fields = [f[0] for f in sf.fields[1:]]

    for sr in sf.shapeRecords():
        shape = sr.shape
        record = dict(zip(fields, sr.record))

        if shape.shapeType != shapefile.POINT:
            continue

        coords = shape.points[0] if shape.points else None
        if not coords:
            continue

        # P30_005: 郵便局名
        name = record.get('P30_005', '') or ''
        # P30_006: 住所
        address = record.get('P30_006', '') or ''

        facilities.append({
            'name': name,
            'address': address,
            'category_code': 'post_office',
            'latitude': coords[1],
            'longitude': coords[0],
            'metadata': {}
        })

    return facilities


def parse_welfare_shapefile(shp_path: Path) -> list:
    """福祉施設Shapefileをパース (P14)"""
    # 福祉施設大分類コード → カテゴリ
    WELFARE_CATEGORIES = {
        16: 'nursery',      # 児童福祉 → 保育所
        19: 'nursing_home', # 高齢者福祉 → 老人ホーム
    }

    facilities = []

    sf = shapefile.Reader(str(shp_path), encoding='cp932')
    fields = [f[0] for f in sf.fields[1:]]

    for sr in sf.shapeRecords():
        shape = sr.shape
        record = dict(zip(fields, sr.record))

        if shape.shapeType != shapefile.POINT:
            continue

        coords = shape.points[0] if shape.points else None
        if not coords:
            continue

        # P14_004: 福祉施設大分類コード
        welfare_code = record.get('P14_004', 0) or 0
        category = WELFARE_CATEGORIES.get(welfare_code, 'welfare')

        # P14_007: 施設名
        name = record.get('P14_007', '') or ''
        # P14_001 + P14_002 + P14_003: 住所
        pref = record.get('P14_001', '') or ''
        city = record.get('P14_002', '') or ''
        addr = record.get('P14_003', '') or ''
        address = '{}{}{}'.format(pref, city, addr)

        facilities.append({
            'name': name,
            'address': address,
            'category_code': category,
            'latitude': coords[1],
            'longitude': coords[0],
            'metadata': {'welfare_code': welfare_code}
        })

    return facilities


def parse_culture_shapefile(shp_path: Path) -> list:
    """文化施設Shapefileをパース (P27)"""
    facilities = []

    sf = shapefile.Reader(str(shp_path), encoding='cp932')
    fields = [f[0] for f in sf.fields[1:]]

    for sr in sf.shapeRecords():
        shape = sr.shape
        record = dict(zip(fields, sr.record))

        if shape.shapeType != shapefile.POINT:
            continue

        coords = shape.points[0] if shape.points else None
        if not coords:
            continue

        # P27_005: 施設名
        name = record.get('P27_005', '') or ''
        # P27_006: 住所
        address = record.get('P27_006', '') or ''

        # 施設名で分類（図書館を特定）
        if '図書館' in name:
            category = 'library'
        else:
            category = 'culture'  # 美術館・博物館等

        facilities.append({
            'name': name,
            'address': address,
            'category_code': category,
            'latitude': coords[1],
            'longitude': coords[0],
            'metadata': {}
        })

    return facilities


def extract_and_parse(zip_path: Path, data_type: str) -> list:
    """ZIPを展開してパース（GeoJSON → Shapefile の順で探す）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)

        tmppath = Path(tmpdir)

        # 1. GeoJSONファイルを優先して探す
        geojson_files = list(tmppath.glob("**/*.geojson"))
        if geojson_files:
            geojson_path = geojson_files[0]
            if data_type == 'P04':
                return parse_medical_geojson(geojson_path)

        # 2. Shapefileを探す
        shp_files = [f for f in tmppath.glob("**/*.shp") if not f.name.startswith("KS-META")]
        if shp_files:
            shp_path = shp_files[0]
            if data_type == 'P13':
                return parse_park_shapefile(shp_path)
            elif data_type == 'P14':
                return parse_welfare_shapefile(shp_path)
            elif data_type == 'P27':
                return parse_culture_shapefile(shp_path)
            elif data_type == 'P30':
                return parse_post_office_shapefile(shp_path)

        return []


def insert_facilities(cur, facilities: list, pref_code: str, data_source: str):
    """施設データをDBに挿入"""
    pref_name = PREFECTURES.get(pref_code, '')

    for facility in facilities:
        try:
            cur.execute("""
                INSERT INTO m_facilities (
                    category_code, name, address,
                    prefecture_code, prefecture_name,
                    latitude, longitude, location,
                    data_source, metadata
                ) VALUES (
                    %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    %s, %s
                )
            """, (
                facility['category_code'], facility['name'], facility['address'],
                pref_code, pref_name,
                facility['latitude'], facility['longitude'],
                facility['longitude'], facility['latitude'],
                data_source, json.dumps(facility.get('metadata', {}))
            ))
        except Exception as e:
            print(f"    挿入エラー: {facility['name']} - {e}")


def import_data_type(data_type: str, description: str):
    """特定のデータタイプをインポート"""
    print(f"\n{'='*60}")
    print(f"国土数値情報 {description}インポート ({data_type})")
    print(f"{'='*60}")

    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        total_count = 0

        for pref_code, pref_name in PREFECTURES.items():
            print(f"\n📍 {pref_name}({pref_code})...")

            zip_path = download_data(data_type, pref_code)
            if not zip_path:
                continue

            facilities = extract_and_parse(zip_path, data_type)
            print(f"  施設数: {len(facilities)}")

            insert_facilities(cur, facilities, pref_code, data_type)
            conn.commit()

            total_count += len(facilities)

        print(f"\n✅ {description}インポート完了: {total_count}件")
        return total_count

    except Exception as e:
        conn.rollback()
        print(f"❌ エラー: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='施設データインポート')
    parser.add_argument('--type', choices=['P04', 'P13', 'P14', 'P27', 'P30', 'all'], default='all',
                       help='インポートするデータタイプ')
    args = parser.parse_args()

    results = {}

    if args.type in ['P04', 'all']:
        results['医療機関'] = import_data_type('P04', '医療機関データ')

    if args.type in ['P13', 'all']:
        results['公園'] = import_data_type('P13', '都市公園データ')

    if args.type in ['P14', 'all']:
        results['福祉施設'] = import_data_type('P14', '福祉施設データ')

    if args.type in ['P27', 'all']:
        results['文化施設'] = import_data_type('P27', '文化施設データ')

    if args.type in ['P30', 'all']:
        results['郵便局'] = import_data_type('P30', '郵便局データ')

    print(f"\n{'='*60}")
    print("インポート結果")
    print(f"{'='*60}")
    for name, count in results.items():
        print(f"  {name}: {count}件")


if __name__ == "__main__":
    main()
