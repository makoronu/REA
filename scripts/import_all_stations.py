#!/usr/bin/env python3
"""
HeartRails Express APIを使って全国の駅データを取得・投入するスクリプト

HeartRails Express API（無料・商用利用可）:
    http://express.heartrails.com/api.html

使用方法:
    cd ~/my_programing/REA
    PYTHONPATH=~/my_programing/REA python3 scripts/import_all_stations.py
"""

import sys
import json
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database import READatabase

# 都道府県リスト
PREFECTURES = [
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
    '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
    '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県',
    '岐阜県', '静岡県', '愛知県', '三重県',
    '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
    '鳥取県', '島根県', '岡山県', '広島県', '山口県',
    '徳島県', '香川県', '愛媛県', '高知県',
    '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
]

# 都道府県コード
PREF_CODES = {
    '北海道': '01', '青森県': '02', '岩手県': '03', '宮城県': '04', '秋田県': '05',
    '山形県': '06', '福島県': '07', '茨城県': '08', '栃木県': '09', '群馬県': '10',
    '埼玉県': '11', '千葉県': '12', '東京都': '13', '神奈川県': '14', '新潟県': '15',
    '富山県': '16', '石川県': '17', '福井県': '18', '山梨県': '19', '長野県': '20',
    '岐阜県': '21', '静岡県': '22', '愛知県': '23', '三重県': '24', '滋賀県': '25',
    '京都府': '26', '大阪府': '27', '兵庫県': '28', '奈良県': '29', '和歌山県': '30',
    '鳥取県': '31', '島根県': '32', '岡山県': '33', '広島県': '34', '山口県': '35',
    '徳島県': '36', '香川県': '37', '愛媛県': '38', '高知県': '39', '福岡県': '40',
    '佐賀県': '41', '長崎県': '42', '熊本県': '43', '大分県': '44', '宮崎県': '45',
    '鹿児島県': '46', '沖縄県': '47'
}

BASE_URL = "http://express.heartrails.com/api/json"


def api_request(params: dict) -> dict:
    """HeartRails Express APIにリクエスト"""
    query = urllib.parse.urlencode(params)
    url = "{}?{}".format(BASE_URL, query)

    req = urllib.request.Request(url, headers={'User-Agent': 'REA/1.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))


def get_lines_by_prefecture(prefecture: str) -> list:
    """都道府県の路線一覧を取得"""
    try:
        data = api_request({'method': 'getLines', 'prefecture': prefecture})
        return data.get('response', {}).get('line', [])
    except Exception as e:
        print("  路線取得エラー ({}): {}".format(prefecture, e))
        return []


def get_stations_by_line(line: str) -> list:
    """路線の駅一覧を取得"""
    try:
        data = api_request({'method': 'getStations', 'line': line})
        return data.get('response', {}).get('station', [])
    except Exception as e:
        print("  駅取得エラー ({}): {}".format(line, e))
        return []


def import_all_stations():
    """全国の駅データを取得してDBに投入"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    # 重複チェック用（駅名+路線名+座標の組み合わせ）
    seen_stations = set()
    all_stations = []

    print("=" * 60)
    print("全国駅データ取得開始")
    print("=" * 60)

    for pref in PREFECTURES:
        pref_code = PREF_CODES[pref]
        print("\n[{}] {} の路線を取得中...".format(pref_code, pref))

        lines = get_lines_by_prefecture(pref)
        print("  {} 路線".format(len(lines)))

        for line in lines:
            stations = get_stations_by_line(line)

            for st in stations:
                # 座標がない駅はスキップ
                if not st.get('x') or not st.get('y'):
                    continue

                # 重複チェック（同じ駅名・路線・座標の組み合わせ）
                key = (st['name'], line, st['x'], st['y'])
                if key in seen_stations:
                    continue
                seen_stations.add(key)

                all_stations.append({
                    'station_name': st['name'],
                    'line_name': line,
                    'longitude': float(st['x']),
                    'latitude': float(st['y']),
                    'prefecture': st.get('prefecture', pref),
                    'prefecture_code': PREF_CODES.get(st.get('prefecture', pref), pref_code)
                })

            # API負荷軽減
            time.sleep(0.1)

        print("  累計: {} 駅".format(len(all_stations)))
        time.sleep(0.2)

    print("\n" + "=" * 60)
    print("DBへの投入開始: {} 駅".format(len(all_stations)))
    print("=" * 60)

    try:
        # 既存データ削除
        cur.execute("DELETE FROM m_stations")
        print("既存データ削除完了")

        # バッチ投入（1000件ずつ）
        batch_size = 1000
        for i in range(0, len(all_stations), batch_size):
            batch = all_stations[i:i + batch_size]

            for st in batch:
                cur.execute("""
                    INSERT INTO m_stations (station_name, line_name, geom, prefecture_code)
                    VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
                """, (
                    st['station_name'],
                    st['line_name'],
                    st['longitude'],
                    st['latitude'],
                    st['prefecture_code']
                ))

            conn.commit()
            print("  {} / {} 件投入完了".format(min(i + batch_size, len(all_stations)), len(all_stations)))

        # 確認
        cur.execute("SELECT COUNT(*) FROM m_stations")
        count = cur.fetchone()[0]
        print("\n✅ 投入完了: {} 駅".format(count))

        # 都道府県別件数
        print("\n都道府県別件数:")
        cur.execute("""
            SELECT prefecture_code, COUNT(*) as cnt
            FROM m_stations
            GROUP BY prefecture_code
            ORDER BY prefecture_code
        """)
        for row in cur.fetchall():
            pref_name = [k for k, v in PREF_CODES.items() if v == row[0]]
            pref_name = pref_name[0] if pref_name else row[0]
            print("  {}: {} 駅".format(pref_name, row[1]))

    except Exception as e:
        conn.rollback()
        print("❌ エラー: {}".format(e))
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    import urllib.parse
    import_all_stations()
