#!/usr/bin/env python3
"""
国土数値情報からバス停留所データをダウンロード・インポート
- P11: バス停留所データ
"""
import os
import sys
import json
import zipfile
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database import READatabase

# データ保存先
DATA_DIR = Path(__file__).parent.parent / "data" / "bus_stops"
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

# バス区分コード
BUS_TYPES = {
    "1": "民間路線バス",
    "2": "公営路線バス",
    "3": "コミュニティバス",
    "4": "デマンドバス",
    "5": "その他"
}


def create_bus_stops_table(cur):
    """バス停テーブル作成"""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS m_bus_stops (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            bus_type VARCHAR(20),
            bus_type_name VARCHAR(50),
            operators TEXT[],
            bus_routes TEXT[],
            prefecture_code VARCHAR(2),
            prefecture_name VARCHAR(20),
            latitude DECIMAL(10, 7),
            longitude DECIMAL(10, 7),
            location GEOMETRY(Point, 4326),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # インデックス作成
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_m_bus_stops_location
        ON m_bus_stops USING GIST (location)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_m_bus_stops_name
        ON m_bus_stops (name)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_m_bus_stops_prefecture
        ON m_bus_stops (prefecture_code)
    """)
    print("✅ m_bus_stops テーブル作成完了")


def download_bus_stop_data(pref_code: str) -> Path:
    """都道府県別のバス停データをダウンロード"""
    # 令和4年度データ (P11-22)
    url = f"https://nlftp.mlit.go.jp/ksj/gml/data/P11/P11-22/P11-22_{pref_code}_GML.zip"
    zip_path = DATA_DIR / f"P11-22_{pref_code}_GML.zip"

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


def parse_gml(gml_path: Path) -> list:
    """GMLファイルをパース"""
    tree = ET.parse(gml_path)
    root = tree.getroot()

    # 名前空間
    ns = {
        'gml': 'http://schemas.opengis.net/gml/3.2.1',
        'ksj': 'http://nlftp.mlit.go.jp/ksj/schemas/ksj-app',
        'xlink': 'http://www.w3.org/1999/xlink'
    }

    # ポイントIDと座標のマッピングを作成
    points = {}
    for point in root.findall('.//gml:Point', ns):
        point_id = point.get('{http://schemas.opengis.net/gml/3.2.1}id')
        pos = point.find('gml:pos', ns)
        if pos is not None and pos.text:
            coords = pos.text.strip().split()
            if len(coords) >= 2:
                # GMLは緯度、経度の順
                points[point_id] = {
                    'latitude': float(coords[0]),
                    'longitude': float(coords[1])
                }

    bus_stops = []
    for bus_stop_elem in root.findall('.//ksj:BusStop', ns):
        # 位置参照を取得
        loc = bus_stop_elem.find('ksj:loc', ns)
        if loc is None:
            continue

        href = loc.get('{http://www.w3.org/1999/xlink}href')
        if not href:
            continue

        point_id = href.lstrip('#')
        if point_id not in points:
            continue

        coords = points[point_id]

        # バス停名
        bsn = bus_stop_elem.find('ksj:bsn', ns)
        name = bsn.text if bsn is not None and bsn.text else ''

        # 事業者名
        boc = bus_stop_elem.find('ksj:boc', ns)
        operator = boc.text if boc is not None and boc.text else ''

        # バス路線情報を収集
        operators = [operator] if operator else []
        routes = []
        bus_type = ''

        for bri in bus_stop_elem.findall('ksj:bri', ns):
            # バス路線名
            brn = bri.find('ksj:brn', ns)
            if brn is not None and brn.text:
                routes.append(brn.text)

            # バス区分（最初のものを使用）
            if not bus_type:
                brt = bri.find('ksj:brt', ns)
                if brt is not None and brt.text:
                    bus_type = brt.text

        bus_stop = {
            'name': name,
            'bus_type': bus_type,
            'operators': operators,
            'routes': routes,
            'longitude': coords['longitude'],
            'latitude': coords['latitude']
        }
        bus_stops.append(bus_stop)

    return bus_stops


def extract_and_parse(zip_path: Path, pref_code: str) -> list:
    """ZIPを展開してパース"""
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)

        tmppath = Path(tmpdir)

        # GMLファイルを探す（KS-META-*以外）
        gml_files = [f for f in tmppath.glob("**/*.xml") if not f.name.startswith("KS-META")]
        if gml_files:
            return parse_gml(gml_files[0])

        return []


def insert_bus_stops(cur, bus_stops: list, pref_code: str):
    """バス停データをDBに挿入"""
    pref_name = PREFECTURES.get(pref_code, '')

    for bus_stop in bus_stops:
        bus_type = bus_stop['bus_type']
        bus_type_name = BUS_TYPES.get(bus_type, '')

        try:
            cur.execute("""
                INSERT INTO m_bus_stops (
                    name, bus_type, bus_type_name, operators, bus_routes,
                    prefecture_code, prefecture_name,
                    latitude, longitude, location
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                )
            """, (
                bus_stop['name'], bus_type, bus_type_name,
                bus_stop['operators'], bus_stop['routes'],
                pref_code, pref_name,
                bus_stop['latitude'], bus_stop['longitude'],
                bus_stop['longitude'], bus_stop['latitude']
            ))
        except Exception as e:
            print(f"    挿入エラー: {bus_stop['name']} - {e}")


def main():
    print("=" * 60)
    print("国土数値情報 バス停留所データインポート")
    print("=" * 60)

    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # テーブル作成（既存テーブルがあればスキップ）
        try:
            create_bus_stops_table(cur)
            conn.commit()
        except Exception as e:
            print(f"テーブル作成スキップ（既存）: {e}")
            conn.rollback()

        # 既存データをクリア
        cur.execute("DELETE FROM m_bus_stops")
        conn.commit()
        print("✅ 既存データクリア")

        total_count = 0

        # 全都道府県を処理
        for pref_code, pref_name in PREFECTURES.items():
            print(f"\n📍 {pref_name}({pref_code})...")

            # ダウンロード
            zip_path = download_bus_stop_data(pref_code)
            if not zip_path:
                continue

            # パース
            bus_stops = extract_and_parse(zip_path, pref_code)
            print(f"  バス停数: {len(bus_stops)}")

            # 挿入
            insert_bus_stops(cur, bus_stops, pref_code)
            conn.commit()

            total_count += len(bus_stops)

        # 最終確認
        cur.execute("SELECT COUNT(*) FROM m_bus_stops")
        db_count = cur.fetchone()[0]

        cur.execute("""
            SELECT bus_type_name, COUNT(*)
            FROM m_bus_stops
            GROUP BY bus_type_name
            ORDER BY bus_type_name
        """)
        type_counts = cur.fetchall()

        print("\n" + "=" * 60)
        print(f"✅ インポート完了: {db_count}件")
        for type_name, count in type_counts:
            print(f"   - {type_name or '不明'}: {count}件")
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
