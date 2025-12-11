#!/usr/bin/env python3
"""
国土数値情報から駅データ（N02）をダウンロードしてPostGISに投入するスクリプト

使用方法:
    cd ~/my_programing/REA
    PYTHONPATH=~/my_programing/REA python scripts/import_stations.py

国土数値情報 N02（鉄道）:
    https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v3_1.html
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


def download_file(url: str, dest_path: str) -> bool:
    """ファイルをダウンロード"""
    print(f"ダウンロード中: {url}")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"ダウンロード完了: {dest_path}")
        return True
    except Exception as e:
        print(f"ダウンロードエラー: {e}")
        return False


def parse_geojson_stations(geojson_path: str) -> list:
    """GeoJSONから駅データを抽出"""
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stations = []
    for feature in data.get('features', []):
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})

        # 駅のみ抽出（N02_004: 駅名がある場合）
        station_name = props.get('N02_005') or props.get('station_name')
        if not station_name:
            continue

        # 座標取得（Point型のみ）
        if geom.get('type') != 'Point':
            continue

        coords = geom.get('coordinates', [])
        if len(coords) < 2:
            continue

        longitude, latitude = coords[0], coords[1]

        stations.append({
            'station_name': station_name,
            'line_name': props.get('N02_003') or props.get('line_name'),
            'company_name': props.get('N02_004') or props.get('company_name'),
            'longitude': longitude,
            'latitude': latitude,
        })

    return stations


def insert_stations_from_csv():
    """
    国土数値情報のデータは複雑なので、
    まずは主要駅のサンプルデータを投入してテストする
    """
    # 主要駅サンプルデータ（東京近郊）
    sample_stations = [
        # 山手線
        ('東京', 'JR山手線', 'JR東日本', 139.7671, 35.6812, '13'),
        ('品川', 'JR山手線', 'JR東日本', 139.7387, 35.6284, '13'),
        ('渋谷', 'JR山手線', 'JR東日本', 139.7016, 35.6580, '13'),
        ('新宿', 'JR山手線', 'JR東日本', 139.7003, 35.6896, '13'),
        ('池袋', 'JR山手線', 'JR東日本', 139.7110, 35.7295, '13'),
        ('上野', 'JR山手線', 'JR東日本', 139.7775, 35.7141, '13'),
        ('秋葉原', 'JR山手線', 'JR東日本', 139.7730, 35.6984, '13'),
        # 中央線
        ('中野', 'JR中央線', 'JR東日本', 139.6655, 35.7061, '13'),
        ('吉祥寺', 'JR中央線', 'JR東日本', 139.5798, 35.7031, '13'),
        ('立川', 'JR中央線', 'JR東日本', 139.4136, 35.6979, '13'),
        ('八王子', 'JR中央線', 'JR東日本', 139.3389, 35.6556, '13'),
        # 京浜東北線
        ('横浜', 'JR京浜東北線', 'JR東日本', 139.6222, 35.4657, '14'),
        ('川崎', 'JR京浜東北線', 'JR東日本', 139.6969, 35.5320, '14'),
        ('大宮', 'JR京浜東北線', 'JR東日本', 139.6234, 35.9064, '11'),
        # 東横線
        ('自由が丘', '東急東横線', '東急電鉄', 139.6691, 35.6072, '13'),
        ('武蔵小杉', '東急東横線', '東急電鉄', 139.6590, 35.5765, '14'),
        # 私鉄
        ('下北沢', '小田急小田原線', '小田急電鉄', 139.6669, 35.6618, '13'),
        ('町田', '小田急小田原線', '小田急電鉄', 139.4461, 35.5421, '13'),
        ('所沢', '西武池袋線', '西武鉄道', 139.4691, 35.7857, '11'),
        ('船橋', 'JR総武線', 'JR東日本', 139.9855, 35.7017, '12'),
        ('柏', 'JR常磐線', 'JR東日本', 139.9719, 35.8597, '12'),
        ('千葉', 'JR総武線', 'JR東日本', 140.1131, 35.6131, '12'),
        # 関西
        ('大阪', 'JR大阪環状線', 'JR西日本', 135.4959, 34.7024, '27'),
        ('梅田', '大阪メトロ御堂筋線', '大阪メトロ', 135.4983, 34.7055, '27'),
        ('難波', '大阪メトロ御堂筋線', '大阪メトロ', 135.5013, 34.6657, '27'),
        ('天王寺', 'JR大阪環状線', 'JR西日本', 135.5147, 34.6469, '27'),
        ('京都', 'JR東海道線', 'JR西日本', 135.7587, 34.9858, '26'),
        ('三ノ宮', 'JR東海道線', 'JR西日本', 135.1939, 34.6953, '28'),
        ('神戸', 'JR東海道線', 'JR西日本', 135.1803, 34.6797, '28'),
        # 名古屋
        ('名古屋', 'JR東海道線', 'JR東海', 136.8815, 35.1709, '23'),
        ('金山', 'JR東海道線', 'JR東海', 136.9003, 35.1429, '23'),
        ('栄', '名古屋市営地下鉄東山線', '名古屋市交通局', 136.9066, 35.1685, '23'),
        # 福岡
        ('博多', 'JR鹿児島本線', 'JR九州', 130.4207, 33.5897, '40'),
        ('天神', '福岡市地下鉄空港線', '福岡市交通局', 130.3988, 33.5913, '40'),
        # 札幌
        ('札幌', 'JR函館本線', 'JR北海道', 141.3509, 43.0687, '01'),
        ('大通', '札幌市営地下鉄南北線', '札幌市交通局', 141.3567, 43.0606, '01'),
        # 仙台
        ('仙台', 'JR東北本線', 'JR東日本', 140.8824, 38.2601, '04'),
        # 広島
        ('広島', 'JR山陽本線', 'JR西日本', 132.4752, 34.3983, '34'),
    ]

    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # 既存データ削除（サンプル投入のため）
        cur.execute("DELETE FROM m_stations")

        # 投入
        for station_name, line_name, company_name, lon, lat, pref in sample_stations:
            cur.execute("""
                INSERT INTO m_stations (station_name, line_name, company_name, geom, prefecture_code)
                VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
            """, (station_name, line_name, company_name, lon, lat, pref))

        conn.commit()
        print(f"✅ {len(sample_stations)}駅を投入しました")

        # 確認
        cur.execute("SELECT COUNT(*) FROM m_stations")
        count = cur.fetchone()[0]
        print(f"   m_stations: {count}件")

        # サンプルクエリ: 渋谷から5km以内の駅
        cur.execute("""
            SELECT station_name, line_name,
                   ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(139.7016, 35.6580), 4326)::geography) as distance_m
            FROM m_stations
            WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(139.7016, 35.6580), 4326)::geography, 5000)
            ORDER BY distance_m
            LIMIT 10
        """)
        print("\n📍 渋谷から5km以内の駅:")
        for row in cur.fetchall():
            print(f"   {row[0]} ({row[1]}) - {row[2]:.0f}m")

    except Exception as e:
        conn.rollback()
        print(f"❌ エラー: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    print("="*50)
    print("駅マスターデータ投入")
    print("="*50)
    insert_stations_from_csv()
