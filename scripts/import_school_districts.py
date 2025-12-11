#!/usr/bin/env python3
"""
国土数値情報から学区ポリゴンデータをダウンロード・インポート
- A27: 小学校区データ
- A32: 中学校区データ
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
DATA_DIR = Path(__file__).parent.parent / "data" / "school_districts"
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


def create_school_districts_table(cur):
    """学区テーブル作成"""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS m_school_districts (
            id SERIAL PRIMARY KEY,
            school_type VARCHAR(20) NOT NULL,
            school_name VARCHAR(200) NOT NULL,
            address VARCHAR(500),
            prefecture_code VARCHAR(2),
            prefecture_name VARCHAR(20),
            admin_type VARCHAR(20),
            area GEOMETRY(MultiPolygon, 4326),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(school_type, school_name, prefecture_code)
        )
    """)

    # 空間インデックス作成
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_m_school_districts_area
        ON m_school_districts USING GIST (area)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_m_school_districts_type
        ON m_school_districts (school_type)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_m_school_districts_prefecture
        ON m_school_districts (prefecture_code)
    """)
    print("✅ m_school_districts テーブル作成完了")


def download_district_data(pref_code: str, school_type: str) -> Path:
    """学区データをダウンロード"""
    if school_type == "elementary":
        # 小学校区: A27-16 (平成28年度)
        url = f"https://nlftp.mlit.go.jp/ksj/gml/data/A27/A27-16/A27-16_{pref_code}_GML.zip"
        filename = f"A27-16_{pref_code}_GML.zip"
    else:
        # 中学校区: A32-16 (平成28年度)
        url = f"https://nlftp.mlit.go.jp/ksj/gml/data/A32/A32-16/A32-16_{pref_code}_GML.zip"
        filename = f"A32-16_{pref_code}_GML.zip"

    zip_path = DATA_DIR / filename

    if zip_path.exists():
        print(f"    キャッシュ使用: {filename}")
        return zip_path

    print(f"    ダウンロード中: {url}")
    try:
        urllib.request.urlretrieve(url, zip_path)
        return zip_path
    except Exception as e:
        print(f"    ⚠ ダウンロード失敗（データなし?）: {e}")
        return None


def parse_shapefile_polygon(shp_dir: Path, prefix: str) -> list:
    """Shapefileのポリゴンをパース"""
    try:
        import shapefile
    except ImportError:
        print("  pyshp未インストール。pip install pyshp を実行してください")
        return []

    # ポリゴンファイルを探す（A27.shp or A32.shp）
    shp_files = list(shp_dir.glob(f"**/{prefix}*.shp"))
    # ポイントファイル（A27P.shp等）は除外
    shp_files = [f for f in shp_files if 'P.shp' not in str(f).upper()]

    if not shp_files:
        return []

    districts = []
    for shp_file in shp_files:
        try:
            sf = shapefile.Reader(str(shp_file), encoding='cp932')
        except:
            try:
                sf = shapefile.Reader(str(shp_file), encoding='utf-8')
            except Exception as e:
                print(f"    読み込みエラー: {shp_file} - {e}")
                continue

        # フィールド名を取得
        fields = [f[0] for f in sf.fields[1:]]

        for sr in sf.shapeRecords():
            props = dict(zip(fields, sr.record))

            # ポリゴンまたはマルチポリゴンのみ
            if sr.shape.shapeType not in [5, 15]:  # Polygon, PolygonZ
                continue

            # Shapefileのポリゴンを GeoJSON形式に変換
            try:
                geojson_geom = sr.shape.__geo_interface__
            except Exception as e:
                continue

            # ポリゴンデータ(A27.shp)の場合: A27_007=名称, A27_008=所在地, A27_006=設置主体
            # A32ポリゴンの場合: A32_007=名称, A32_008=所在地, A32_006=設置主体
            if 'A27_007' in props:
                name_key, addr_key, admin_key = 'A27_007', 'A27_008', 'A27_006'
            elif 'A32_007' in props:
                name_key, addr_key, admin_key = 'A32_007', 'A32_008', 'A32_006'
            else:
                continue  # 対応するフィールドがない場合はスキップ

            district = {
                'name': str(props.get(name_key, '')),
                'address': str(props.get(addr_key, '')),
                'admin_type': str(props.get(admin_key, '')),
                'geometry': geojson_geom
            }
            districts.append(district)

    return districts


def extract_and_parse(zip_path: Path, prefix: str) -> list:
    """ZIPを展開してパース"""
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmpdir)
        except Exception as e:
            print(f"    ZIP展開エラー: {e}")
            return []

        tmppath = Path(tmpdir)
        return parse_shapefile_polygon(tmppath, prefix)


def geometry_to_wkt_multipolygon(geom: dict) -> str:
    """GeoJSON geometryをWKT MultiPolygonに変換"""
    geom_type = geom.get('type', '')
    coords = geom.get('coordinates', [])

    if geom_type == 'Polygon':
        # Polygon を MultiPolygon に変換
        rings = []
        for ring in coords:
            points = ', '.join(f"{p[0]} {p[1]}" for p in ring)
            rings.append(f"(({points}))")
        return f"MULTIPOLYGON({','.join(rings)})"

    elif geom_type == 'MultiPolygon':
        polygons = []
        for polygon in coords:
            rings = []
            for ring in polygon:
                points = ', '.join(f"{p[0]} {p[1]}" for p in ring)
                rings.append(f"({points})")
            polygons.append(f"({','.join(rings)})")
        return f"MULTIPOLYGON({','.join(polygons)})"

    return None


def insert_districts(cur, districts: list, pref_code: str, school_type: str):
    """学区データをDBに挿入"""
    pref_name = PREFECTURES.get(pref_code, '')
    type_name = "小学校" if school_type == "elementary" else "中学校"

    inserted = 0
    for district in districts:
        if not district['name']:
            continue

        wkt = geometry_to_wkt_multipolygon(district['geometry'])
        if not wkt:
            continue

        try:
            cur.execute("""
                INSERT INTO m_school_districts (
                    school_type, school_name, address,
                    prefecture_code, prefecture_name, admin_type, area
                ) VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    ST_SetSRID(ST_GeomFromText(%s), 4326)
                )
                ON CONFLICT (school_type, school_name, prefecture_code) DO UPDATE SET
                    address = EXCLUDED.address,
                    admin_type = EXCLUDED.admin_type,
                    area = EXCLUDED.area
            """, (
                type_name, district['name'], district['address'],
                pref_code, pref_name, district['admin_type'], wkt
            ))
            inserted += 1
        except Exception as e:
            # エラー詳細は省略（大量に出るため）
            pass

    return inserted


def main():
    print("=" * 60)
    print("国土数値情報 学区ポリゴンデータインポート")
    print("=" * 60)

    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # テーブル作成
        create_school_districts_table(cur)
        conn.commit()

        total_elementary = 0
        total_junior_high = 0

        # 全都道府県を処理
        for pref_code, pref_name in PREFECTURES.items():
            print(f"\n📍 {pref_name}({pref_code})...")

            # 小学校区
            print("  [小学校区]")
            zip_path = download_district_data(pref_code, "elementary")
            if zip_path:
                districts = extract_and_parse(zip_path, "A27")
                print(f"    学区数: {len(districts)}")
                inserted = insert_districts(cur, districts, pref_code, "elementary")
                total_elementary += inserted
                conn.commit()

            # 中学校区
            print("  [中学校区]")
            zip_path = download_district_data(pref_code, "junior_high")
            if zip_path:
                districts = extract_and_parse(zip_path, "A32")
                print(f"    学区数: {len(districts)}")
                inserted = insert_districts(cur, districts, pref_code, "junior_high")
                total_junior_high += inserted
                conn.commit()

        # 最終確認
        cur.execute("""
            SELECT school_type, COUNT(*)
            FROM m_school_districts
            GROUP BY school_type
            ORDER BY school_type
        """)
        type_counts = cur.fetchall()

        print("\n" + "=" * 60)
        print(f"✅ インポート完了")
        for type_name, count in type_counts:
            print(f"   - {type_name}: {count}学区")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
