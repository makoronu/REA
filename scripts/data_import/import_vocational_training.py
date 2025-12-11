#!/usr/bin/env python3
"""
職業訓練校データインポートスクリプト

データソース: 各都道府県の公式サイト（手動収集）
URL: https://www.pref.hokkaido.lg.jp/kz/jzi/69081.html (北海道)

対象:
- 都道府県立職業能力開発校（高等技術専門学院、テクノスクール等）
- 全国166校

注意:
- 公式CSVデータなし、手動で住所・座標を収集
- 現在は北海道8校のみ登録済み
- 他県は順次追加が必要

使用方法:
    cd ~/my_programing/REA
    PYTHONPATH=~/my_programing/REA python3 scripts/data_import/import_vocational_training.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))
from shared.database import READatabase

# 職業訓練校データ（手動収集）
# TODO: 他県のデータを追加
VOCATIONAL_TRAINING_SCHOOLS = [
    # 北海道（MONOテク）8校
    {'name': '札幌高等技術専門学院', 'address': '北海道札幌市東区北27条東16丁目1-1', 'pref_code': '01', 'pref_name': '北海道', 'lat': 43.09867, 'lon': 141.36486},
    {'name': '函館高等技術専門学院', 'address': '北海道函館市桔梗町435', 'pref_code': '01', 'pref_name': '北海道', 'lat': 41.84147, 'lon': 140.75583},
    {'name': '旭川高等技術専門学院', 'address': '北海道旭川市緑が丘東3条2丁目1-1', 'pref_code': '01', 'pref_name': '北海道', 'lat': 43.78056, 'lon': 142.39028},
    {'name': '北見高等技術専門学院', 'address': '北海道北見市末広町356-1', 'pref_code': '01', 'pref_name': '北海道', 'lat': 43.82500, 'lon': 143.89167},
    {'name': '室蘭高等技術専門学院', 'address': '北海道室蘭市みゆき町2丁目8-3', 'pref_code': '01', 'pref_name': '北海道', 'lat': 42.35278, 'lon': 140.97361},
    {'name': '苫小牧高等技術専門学院', 'address': '北海道苫小牧市新開町4丁目6-12', 'pref_code': '01', 'pref_name': '北海道', 'lat': 42.63694, 'lon': 141.60528},
    {'name': '帯広高等技術専門学院', 'address': '北海道帯広市西21条北2丁目1-13', 'pref_code': '01', 'pref_name': '北海道', 'lat': 42.93028, 'lon': 143.16500},
    {'name': '釧路高等技術専門学院', 'address': '北海道釧路市大楽毛南1丁目2-11', 'pref_code': '01', 'pref_name': '北海道', 'lat': 42.97611, 'lon': 144.32944},

    # TODO: 青森県、岩手県、宮城県...と追加していく
]


def import_data():
    """データをDBにインポート"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    # カテゴリ追加
    cur.execute("""
        INSERT INTO m_facility_categories (category_code, category_name, icon, display_order)
        VALUES ('vocational_training', '職業訓練校', '🏭', 9)
        ON CONFLICT (category_code) DO UPDATE SET display_order = 9
    """)

    # 既存データ削除（再投入のため）
    cur.execute("DELETE FROM m_facilities WHERE category_code = 'vocational_training'")
    deleted = cur.rowcount
    print(f"既存データ削除: {deleted}件")

    # データ投入
    for school in VOCATIONAL_TRAINING_SCHOOLS:
        cur.execute("""
            INSERT INTO m_facilities (category_code, name, address, prefecture_code, prefecture_name,
                                      latitude, longitude, location, data_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
        """, ('vocational_training', school['name'], school['address'],
              school['pref_code'], school['pref_name'],
              school['lat'], school['lon'], school['lon'], school['lat'], 'manual'))

    conn.commit()
    print(f"投入完了: {len(VOCATIONAL_TRAINING_SCHOOLS)}件")

    # データソーステーブル更新
    cur.execute("""
        UPDATE m_data_sources
        SET record_count = %s, last_updated = CURRENT_DATE, updated_at = CURRENT_TIMESTAMP
        WHERE category_code = 'vocational_training'
    """, (len(VOCATIONAL_TRAINING_SCHOOLS),))
    conn.commit()

    cur.close()
    conn.close()


if __name__ == '__main__':
    import_data()
