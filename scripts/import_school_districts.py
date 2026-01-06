#!/usr/bin/env python3
"""
国土数値情報 A27（小学校区データ）をm_school_districtsテーブルに投入するスクリプト
Shapefile形式を読み込み
"""

import json
import os
import sys
import zipfile
import tempfile
import urllib.request

import psycopg2
import shapefile  # pyshp

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

def download_prefecture_data(pref_code, temp_dir):
    url = f"https://nlftp.mlit.go.jp/ksj/gml/data/A27/A27-16/A27-16_{pref_code}_GML.zip"
    zip_path = os.path.join(temp_dir, f"A27-16_{pref_code}.zip")
    print(f"  ダウンロード: {url}")
    try:
        urllib.request.urlretrieve(url, zip_path)
        return zip_path
    except Exception as e:
        print(f"  エラー: {e}")
        return None

def extract_shapefile(zip_path, temp_dir):
    """Shapefile関連ファイルを展開し、.shpファイルのパスを返す"""
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # 必要な拡張子: .shp, .shx, .dbf, .prj
        shp_path = None
        for name in zf.namelist():
            # A27-xx_xx.shp (ポリゴン版) のみ取得、A27P-xx_xx.shp (ポイント版)は除外
            if name.endswith(('.shp', '.shx', '.dbf', '.prj', '.cpg')):
                zf.extract(name, temp_dir)
                # A27-で始まる（A27P-ではない）.shpを探す
                if name.endswith('.shp') and '/A27-' in name and '/A27P-' not in name:
                    shp_path = os.path.join(temp_dir, name)
        return shp_path

def shape_to_geojson(shape):
    """pyshpのShapeをGeoJSON形式に変換"""
    # POLYGON, POLYGONZ, POLYGONMを処理
    if shape.shapeType in (shapefile.POLYGON, shapefile.POLYGONZ, shapefile.POLYGONM):
        parts = list(shape.parts) + [len(shape.points)]
        rings = []
        for i in range(len(parts) - 1):
            ring = []
            for pt in shape.points[parts[i]:parts[i+1]]:
                # Z座標があっても最初の2つ（x, y）だけ使用
                ring.append([pt[0], pt[1]])
            rings.append(ring)
        if len(rings) == 1:
            return {"type": "Polygon", "coordinates": [rings[0]]}
        else:
            return {"type": "Polygon", "coordinates": rings}
    return None

def import_shapefile(shp_path, pref_code, conn):
    """Shapefileを読み込んでDBに投入"""
    sf = shapefile.Reader(shp_path, encoding='cp932')

    # フィールド名を取得
    fields = [f[0] for f in sf.fields[1:]]  # 最初のDeletionFlagをスキップ

    cur = conn.cursor()
    count = 0

    for sr in sf.shapeRecords():
        shape = sr.shape
        rec = sr.record

        # レコードを辞書に変換
        props = dict(zip(fields, rec))

        # PolygonまたはMultiPolygonのみ
        if shape.shapeType not in (shapefile.POLYGON, shapefile.POLYGONZ, shapefile.POLYGONM):
            continue

        # A27_007: 学校名
        school_name = str(props.get('A27_007', '') or '')
        if not school_name:
            continue

        # A27は小学校区のみ
        school_type = '小学校'
        prefecture = PREFECTURE_CODES.get(pref_code, '')

        # A27_006: 設置者名（例：「中央区立」）から市区町村を推定
        admin_name = str(props.get('A27_006', '') or '')
        city = admin_name.replace('立', '') if admin_name else ''

        # ShapeをGeoJSONに変換
        geom = shape_to_geojson(shape)
        if not geom:
            continue

        geojson_str = json.dumps(geom)

        try:
            cur.execute("""
                INSERT INTO m_school_districts (school_name, school_type, area, prefecture, city)
                VALUES (%s, %s, ST_Multi(ST_GeomFromGeoJSON(%s)), %s, %s)
            """, (school_name, school_type, geojson_str, prefecture, city))
            count += 1
        except Exception as e:
            print(f"    挿入エラー: {school_name} - {e}")

    conn.commit()
    return count

def main():
    conn = get_db_connection()
    
    cur = conn.cursor()
    cur.execute("DELETE FROM m_school_districts")
    conn.commit()
    print("既存データクリア")
    
    total = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for pref_code, pref_name in PREFECTURE_CODES.items():
            print(f"\n{pref_name} ({pref_code})")
            
            zip_path = download_prefecture_data(pref_code, temp_dir)
            if not zip_path:
                continue

            shp_path = extract_shapefile(zip_path, temp_dir)
            if not shp_path:
                print("  Shapefileなし")
                continue

            count = import_shapefile(shp_path, pref_code, conn)
            print(f"  {count} 件")
            total += count

            try:
                os.remove(zip_path)
                # Shapefile関連ファイルも削除
                base = shp_path[:-4]
                for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                    try:
                        os.remove(base + ext)
                    except:
                        pass
            except:
                pass
    
    print(f"\n合計: {total} 件の小学校区")
    
    cur.execute("SELECT COUNT(*) FROM m_school_districts")
    print(f"DB内: {cur.fetchone()[0]} 件")
    
    conn.close()

if __name__ == '__main__':
    main()
