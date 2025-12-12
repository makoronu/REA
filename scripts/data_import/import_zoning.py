#!/usr/bin/env python3
"""
用途地域データインポートスクリプト

データソース: 国土数値情報 用途地域データ (A29)
URL: https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-A29-v2_1.html
形式: Shapefile (A29-19_XX.shp) ※令和元年(2019)版

属性（v2.1）:
- A29_001: 行政区域コード
- A29_002: 都道府県名
- A29_003: 市区町村名
- A29_004: 用途地域分類コード
- A29_005: 用途地域名
- A29_006: 建ぺい率（%）
- A29_007: 容積率（%）
- A29_008: 備考

用途地域分類コード:
1:第一種低層住居専用地域, 2:第二種低層住居専用地域, 3:第一種中高層住居専用地域,
4:第二種中高層住居専用地域, 5:第一種住居地域, 6:第二種住居地域, 7:準住居地域,
8:近隣商業地域, 9:商業地域, 10:準工業地域, 11:工業地域, 12:工業専用地域,
21:田園住居地域, 99:不明

使用方法:
    # 全国一括
    cd ~/my_programing/REA
    PYTHONPATH=~/my_programing/REA python3 scripts/data_import/import_zoning.py

    # 特定の都道府県のみ（北海道=01, 東京=13など）
    PYTHONPATH=~/my_programing/REA python3 scripts/data_import/import_zoning.py 01 13
"""

import os
import sys
import urllib.request
import zipfile
from pathlib import Path

import shapefile

sys.path.insert(0, str(Path(__file__).parents[2]))
from shared.database import READatabase

# ダウンロードURLベース（令和元年=2019版）
BASE_URL = "https://nlftp.mlit.go.jp/ksj/gml/data/A29/A29-19"
DATA_DIR = Path(__file__).parents[2] / "data" / "mlit_zoning"
DATA_VERSION = "19"  # 令和元年=2019

# 都道府県コード
PREF_CODES = [
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
    '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
    '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
    '31', '32', '33', '34', '35', '36', '37', '38', '39', '40',
    '41', '42', '43', '44', '45', '46', '47'
]

# 用途地域分類コード→名称
ZONE_NAMES = {
    1: '第一種低層住居専用地域',
    2: '第二種低層住居専用地域',
    3: '第一種中高層住居専用地域',
    4: '第二種中高層住居専用地域',
    5: '第一種住居地域',
    6: '第二種住居地域',
    7: '準住居地域',
    8: '近隣商業地域',
    9: '商業地域',
    10: '準工業地域',
    11: '工業地域',
    12: '工業専用地域',
    21: '田園住居地域',
    99: '不明'
}


def download_prefecture(pref_code: str, force_download: bool = False) -> Path:
    """都道府県のデータをダウンロード"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    zip_name = f"A29-{DATA_VERSION}_{pref_code}_GML.zip"
    zip_path = DATA_DIR / zip_name
    extract_dir = DATA_DIR / f"A29-{DATA_VERSION}_{pref_code}"

    if extract_dir.exists() and not force_download:
        print(f"既存データを使用: {extract_dir}")
        return extract_dir

    url = f"{BASE_URL}/{zip_name}"
    print(f"ダウンロード中: {url}")

    req = urllib.request.Request(url, headers={'User-Agent': 'REA/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            with open(zip_path, 'wb') as f:
                f.write(response.read())
    except urllib.error.HTTPError as e:
        print(f"  -> ダウンロード失敗（{e.code}）: {pref_code}")
        return None

    print(f"解凍中: {zip_path}")
    # 日本語ファイル名対応で解凍
    with zipfile.ZipFile(zip_path, 'r') as z:
        for info in z.infolist():
            # CP932でデコード
            try:
                fixed_name = info.filename.encode('cp437').decode('cp932')
            except:
                fixed_name = info.filename

            # 安全なファイル名に変換
            safe_name = fixed_name.replace('シェープファイル形式', 'shp').replace('GeoJSON形式', 'geojson').replace('メタデータ', 'meta').replace('XML形式', 'xml')
            target_path = extract_dir / safe_name

            if info.is_dir():
                target_path.mkdir(parents=True, exist_ok=True)
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, open(target_path, 'wb') as dst:
                    dst.write(src.read())

    # ZIPファイル削除
    zip_path.unlink()

    return extract_dir


def find_shapefiles(extract_dir: Path) -> list:
    """解凍したディレクトリから全Shapefileを探す（市区町村ごとに分かれている）"""
    shapefiles = list(extract_dir.rglob("*.shp"))
    return sorted(shapefiles)


def import_shapefile(shp_path: Path, cur, conn) -> int:
    """Shapefileをインポート"""
    sf = shapefile.Reader(str(shp_path), encoding='cp932')

    inserted = 0
    for sr in sf.shapeRecords():
        rec = sr.record
        shape = sr.shape

        # 属性取得（v2.1: A29_001〜A29_008の8項目）
        admin_code = rec[0] if len(rec) > 0 else None
        pref_name = rec[1] if len(rec) > 1 else None
        city_name = rec[2] if len(rec) > 2 else None
        zone_code = int(rec[3]) if len(rec) > 3 and rec[3] else None
        zone_name = rec[4] if len(rec) > 4 else ZONE_NAMES.get(zone_code, '')
        bcr = int(rec[5]) if len(rec) > 5 and rec[5] else None  # 建ぺい率
        far = int(rec[6]) if len(rec) > 6 and rec[6] else None  # 容積率
        remarks = rec[7] if len(rec) > 7 else None  # v2.1では備考がA29_008
        source_org = None  # v2.1では無し
        source_year = 2019  # データ年度は固定

        # ジオメトリをWKT形式に変換
        if shape.shapeType == shapefile.POLYGON:
            # シングルポリゴン
            parts = list(shape.parts) + [len(shape.points)]
            rings = []
            for i in range(len(parts) - 1):
                ring = shape.points[parts[i]:parts[i+1]]
                ring_wkt = ','.join([f'{p[0]} {p[1]}' for p in ring])
                rings.append(f'(({ring_wkt}))')
            wkt = f"MULTIPOLYGON({','.join(rings)})"
        elif shape.shapeType == shapefile.NULL:
            continue
        else:
            # その他の形状は処理をスキップ
            continue

        try:
            cur.execute("""
                INSERT INTO m_zoning (
                    admin_code, prefecture_name, city_name, zone_code, zone_name,
                    building_coverage_ratio, floor_area_ratio, source_org, source_year, remarks,
                    geom
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    ST_Multi(ST_SetSRID(ST_GeomFromText(%s), 4326))
                )
            """, (admin_code, pref_name, city_name, zone_code, zone_name,
                  bcr, far, source_org, source_year, remarks, wkt))
            inserted += 1
        except Exception as e:
            print(f"  Insert error: {e}")
            conn.rollback()
            continue

        if inserted % 1000 == 0:
            print(f"    {inserted}件投入...")
            conn.commit()

    conn.commit()
    return inserted


def import_prefecture(pref_code: str, cur, conn, force_download: bool = False) -> int:
    """都道府県のデータをインポート"""
    extract_dir = download_prefecture(pref_code, force_download)
    if not extract_dir:
        return 0

    shp_files = find_shapefiles(extract_dir)
    if not shp_files:
        print(f"  -> Shapefile not found in {extract_dir}")
        return 0

    print(f"インポート中: {len(shp_files)}個のShapefile")
    total = 0
    for shp_path in shp_files:
        count = import_shapefile(shp_path, cur, conn)
        total += count
    return total


def main(target_prefs=None):
    """メイン処理"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    # 対象都道府県
    prefs = target_prefs if target_prefs else PREF_CODES

    # 既存データ削除（対象都道府県のみ）
    for pref in prefs:
        cur.execute("DELETE FROM m_zoning WHERE admin_code LIKE %s", (f'{pref}%',))
    conn.commit()
    print(f"既存データ削除完了（{len(prefs)}都道府県）")

    # インポート
    total = 0
    for pref in prefs:
        print(f"\n[{pref}] 処理開始...")
        count = import_prefecture(pref, cur, conn)
        print(f"[{pref}] 完了: {count}件")
        total += count

    print(f"\n=== 総計: {total}件投入 ===")

    # データソース更新
    try:
        # 既存レコードを更新、なければ挿入
        cur.execute("""
            UPDATE m_data_sources
            SET last_updated = CURRENT_DATE, record_count = %s, updated_at = CURRENT_TIMESTAMP
            WHERE source_name = '国土数値情報 用途地域データ'
        """, (total,))
        if cur.rowcount == 0:
            cur.execute("""
                INSERT INTO m_data_sources (source_name, source_url, category_code, last_updated, record_count)
                VALUES ('国土数値情報 用途地域データ', 'https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-A29.html', 'zoning', CURRENT_DATE, %s)
            """, (total,))
        conn.commit()
    except Exception as e:
        print(f"データソース更新エラー（無視）: {e}")
        conn.rollback()

    cur.close()
    conn.close()


if __name__ == '__main__':
    # コマンドライン引数で都道府県コードを指定可能
    if len(sys.argv) > 1:
        target_prefs = sys.argv[1:]
        print(f"対象都道府県: {target_prefs}")
        main(target_prefs)
    else:
        print("全国データをインポート（時間がかかります）")
        main()
