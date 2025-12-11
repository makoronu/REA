#!/usr/bin/env python3
"""
OpenStreetMapから施設データをインポート
- スーパーマーケット (shop=supermarket)
- コンビニ (shop=convenience)
- ホームセンター (shop=doityourself)
- ドラッグストア (shop=chemist, amenity=pharmacy)
"""
import os
import sys
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database import READatabase

# Overpass APIエンドポイント
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# 施設カテゴリ定義
FACILITY_TYPES = {
    'supermarket': {
        'name': 'スーパー',
        'query': '[shop=supermarket]',
        'category_code': 'supermarket'
    },
    'convenience': {
        'name': 'コンビニ',
        'query': '[shop=convenience]',
        'category_code': 'convenience'
    },
    'doityourself': {
        'name': 'ホームセンター',
        'query': '[shop=doityourself]',
        'category_code': 'home_center'
    },
    'drugstore': {
        'name': 'ドラッグストア',
        'query': '[shop=chemist]',
        'category_code': 'drugstore'
    }
}


def fetch_osm_data(facility_type: str) -> list:
    """Overpass APIから日本全域の施設データを取得"""
    config = FACILITY_TYPES[facility_type]
    print(f"\n📍 {config['name']}データを取得中...")

    # 日本全域のバウンディングボックス
    # (south, west, north, east)
    japan_bbox = "24.0,122.0,46.0,154.0"

    query = f"""
    [out:json][timeout:300];
    area["ISO3166-1"="JP"]->.japan;
    (
      node{config['query']}(area.japan);
      way{config['query']}(area.japan);
    );
    out center;
    """

    print(f"  クエリ実行中（最大5分）...")

    try:
        data = urllib.parse.urlencode({'data': query}).encode('utf-8')
        req = urllib.request.Request(OVERPASS_URL, data=data)
        req.add_header('User-Agent', 'REA-FacilityImporter/1.0')

        with urllib.request.urlopen(req, timeout=600) as response:
            result = json.loads(response.read().decode('utf-8'))

        elements = result.get('elements', [])
        print(f"  取得件数: {len(elements)}")
        return elements

    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return []


def parse_osm_element(element: dict, category_code: str) -> dict:
    """OSM要素をパース"""
    tags = element.get('tags', {})

    # 座標取得（nodeの場合とway/relationの場合で異なる）
    if element['type'] == 'node':
        lat = element.get('lat')
        lon = element.get('lon')
    else:
        # way/relationはcenterを使用
        center = element.get('center', {})
        lat = center.get('lat')
        lon = center.get('lon')

    if not lat or not lon:
        return None

    # 名前（日本語優先）
    name = tags.get('name:ja') or tags.get('name') or ''

    # ブランド名（コンビニ等で使用）
    brand = tags.get('brand:ja') or tags.get('brand') or ''
    if not name and brand:
        name = brand

    # 住所
    addr_parts = []
    if tags.get('addr:province'):
        addr_parts.append(tags['addr:province'])
    if tags.get('addr:city'):
        addr_parts.append(tags['addr:city'])
    if tags.get('addr:suburb'):
        addr_parts.append(tags['addr:suburb'])
    if tags.get('addr:quarter'):
        addr_parts.append(tags['addr:quarter'])
    if tags.get('addr:neighbourhood'):
        addr_parts.append(tags['addr:neighbourhood'])
    if tags.get('addr:block_number'):
        addr_parts.append(tags['addr:block_number'])
    if tags.get('addr:housenumber'):
        addr_parts.append(tags['addr:housenumber'])

    address = ''.join(addr_parts) or tags.get('addr:full', '')

    return {
        'name': name,
        'address': address,
        'category_code': category_code,
        'latitude': lat,
        'longitude': lon,
        'metadata': {
            'osm_id': element.get('id'),
            'osm_type': element.get('type'),
            'brand': brand,
            'operator': tags.get('operator', ''),
            'opening_hours': tags.get('opening_hours', '')
        }
    }


def insert_facilities(facilities: list, data_source: str):
    """施設データをDBに挿入"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    inserted = 0
    skipped = 0

    try:
        for facility in facilities:
            if not facility:
                skipped += 1
                continue

            try:
                cur.execute("""
                    INSERT INTO m_facilities (
                        category_code, name, address,
                        latitude, longitude, location,
                        data_source, metadata
                    ) VALUES (
                        %s, %s, %s,
                        %s, %s,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                        %s, %s
                    )
                    ON CONFLICT DO NOTHING
                """, (
                    facility['category_code'],
                    facility['name'],
                    facility['address'],
                    facility['latitude'],
                    facility['longitude'],
                    facility['longitude'],
                    facility['latitude'],
                    data_source,
                    json.dumps(facility.get('metadata', {}))
                ))
                inserted += 1
            except Exception as e:
                print(f"    挿入エラー: {facility.get('name', 'unknown')} - {e}")
                skipped += 1

        conn.commit()
        print(f"  ✅ 挿入完了: {inserted}件 (スキップ: {skipped}件)")
        return inserted

    except Exception as e:
        conn.rollback()
        print(f"  ❌ エラー: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def import_facility_type(facility_type: str):
    """特定の施設タイプをインポート"""
    config = FACILITY_TYPES[facility_type]
    print(f"\n{'='*60}")
    print(f"{config['name']}データインポート")
    print(f"{'='*60}")

    # OSMからデータ取得
    elements = fetch_osm_data(facility_type)
    if not elements:
        print("  データなし")
        return 0

    # パース
    facilities = [parse_osm_element(e, config['category_code']) for e in elements]
    facilities = [f for f in facilities if f]  # None除去

    print(f"  有効データ: {len(facilities)}件")

    # DB挿入
    count = insert_facilities(facilities, f"OSM-{facility_type}")

    # API負荷軽減のため待機
    print("  API負荷軽減のため10秒待機...")
    time.sleep(10)

    return count


def main():
    import argparse
    parser = argparse.ArgumentParser(description='OSM施設データインポート')
    parser.add_argument('--type',
                       choices=['supermarket', 'convenience', 'doityourself', 'drugstore', 'all'],
                       default='all',
                       help='インポートする施設タイプ')
    args = parser.parse_args()

    results = {}

    types_to_import = FACILITY_TYPES.keys() if args.type == 'all' else [args.type]

    for ftype in types_to_import:
        try:
            results[FACILITY_TYPES[ftype]['name']] = import_facility_type(ftype)
        except Exception as e:
            print(f"❌ {FACILITY_TYPES[ftype]['name']}インポート失敗: {e}")
            results[FACILITY_TYPES[ftype]['name']] = 0

    print(f"\n{'='*60}")
    print("インポート結果")
    print(f"{'='*60}")
    for name, count in results.items():
        print(f"  {name}: {count}件")


if __name__ == "__main__":
    main()
