#!/usr/bin/env python3
"""
都市計画区域データ（国土数値情報 A09）インポートスクリプト

データソース: https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-A09.html
layer_no コード:
  1: 市街化区域
  2: 市街化調整区域
  3: その他用途地域
  4: 用途未設定
"""

import sys
import os
import urllib.request
import zipfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))
from shared.database import READatabase

# 都市計画区域コード
URBAN_PLANNING_CODES = {
    1: '市街化区域',
    2: '市街化調整区域',
    3: 'その他用途地域',
    4: '用途未設定',
}

# 都道府県コード（まず北海道のみ）
PREFECTURES = {
    '01': '北海道',
}

def create_table():
    """m_urban_planningテーブルを作成"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS m_urban_planning (
                id SERIAL PRIMARY KEY,
                admin_code VARCHAR(10),
                prefecture_name VARCHAR(20),
                city_name VARCHAR(50),
                layer_no INTEGER,
                area_type VARCHAR(50),
                geom GEOMETRY(MULTIPOLYGON, 4326),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # インデックス作成
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_urban_planning_geom
            ON m_urban_planning USING GIST(geom)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_urban_planning_layer
            ON m_urban_planning(layer_no)
        """)

        conn.commit()
        print("✅ m_urban_planning テーブル作成完了")

    finally:
        cur.close()
        conn.close()


def download_and_extract(pref_code: str) -> str:
    """Shapefileをダウンロード・展開"""
    # 2018年版のShapefile
    url = f"https://nlftp.mlit.go.jp/ksj/gml/data/A09/A09-18/A09-18_{pref_code}_GML.zip"

    print(f"📥 ダウンロード中: {url}")

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "data.zip")

    req = urllib.request.Request(url, headers={'User-Agent': 'REA/1.0'})
    with urllib.request.urlopen(req, timeout=120) as response:
        with open(zip_path, 'wb') as f:
            f.write(response.read())

    # 展開
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(temp_dir)

    print(f"✅ 展開完了: {temp_dir}")
    return temp_dir


def find_shapefiles(directory: str) -> list:
    """全Shapefileを探す（市区町村ごとに分かれている）"""
    shapefiles = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.shp'):
                shapefiles.append(os.path.join(root, f))
    if not shapefiles:
        raise FileNotFoundError("Shapefileが見つかりません")
    return shapefiles


def import_shapefile(shp_path: str, pref_code: str):
    """ShapefileをDBにインポート"""
    import shapefile

    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    pref_name = PREFECTURES.get(pref_code, '')

    try:
        sf = shapefile.Reader(shp_path, encoding='cp932')

        # フィールド: prefec_cd, area_cd, layer_no
        inserted = 0

        for shape, rec in zip(sf.shapes(), sf.records()):
            prefec_cd = rec[0]  # 都道府県コード
            area_cd = rec[1]    # 市区町村コード
            layer_no = rec[2]   # 都市計画区分

            # layer_noを整数に変換
            try:
                layer_no = int(layer_no) if layer_no else None
            except (ValueError, TypeError):
                layer_no = None

            area_type = URBAN_PLANNING_CODES.get(layer_no, '不明')

            # ポリゴンをWKTに変換
            if shape.shapeType in (5, 15, 25):  # Polygon, PolygonZ, PolygonM
                try:
                    wkt = shape_to_wkt(shape)
                    if wkt:
                        cur.execute("""
                            INSERT INTO m_urban_planning
                            (admin_code, prefecture_name, layer_no, area_type, geom)
                            VALUES (%s, %s, %s, %s, ST_GeomFromText(%s, 4326))
                        """, (str(area_cd), pref_name, layer_no, area_type, wkt))
                        inserted += 1
                except Exception as e:
                    pass  # ポリゴン変換エラーは無視

        conn.commit()
        if inserted > 0:
            print(f"  ✅ {inserted}件")

    finally:
        cur.close()
        conn.close()


def shape_to_wkt(shape) -> str:
    """ShapeをWKT MULTIPOLYGON形式に変換"""
    points = shape.points
    parts = list(shape.parts) + [len(points)]

    polygons = []
    for i in range(len(parts) - 1):
        start = parts[i]
        end = parts[i + 1]
        ring_points = points[start:end]

        if len(ring_points) >= 4:
            coords = ', '.join(f"{p[0]} {p[1]}" for p in ring_points)
            polygons.append(f"(({coords}))")

    if polygons:
        return f"MULTIPOLYGON({', '.join(polygons)})"
    return None


def main():
    print("=" * 60)
    print("都市計画区域データ インポート")
    print("=" * 60)

    # pyshpインストール確認
    try:
        import shapefile
    except ImportError:
        print("❌ pyshpが必要です: pip install pyshp")
        return

    # テーブル作成
    create_table()

    # 北海道のみインポート
    for pref_code, pref_name in PREFECTURES.items():
        print(f"\n📍 {pref_name} ({pref_code})")

        try:
            temp_dir = download_and_extract(pref_code)
            shp_files = find_shapefiles(temp_dir)
            print(f"📄 {len(shp_files)}個のShapefileを検出")
            for shp_path in shp_files:
                import_shapefile(shp_path, pref_code)
        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()

    # 結果確認
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT area_type, COUNT(*)
            FROM m_urban_planning
            GROUP BY area_type
            ORDER BY COUNT(*) DESC
        """)
        print("\n📊 インポート結果:")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]}件")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
