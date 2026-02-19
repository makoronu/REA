"""
地理情報API（書き込みエンドポイント）

読み取り専用エンドポイントはGeo API (:8007) に移行済み。
ここにはDB書き込みを伴うPOSTエンドポイントのみ残す。
"""

import logging
from fastapi import APIRouter, Query, HTTPException
import json
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parents[5]))
from shared.database import READatabase
from shared.constants import calc_walk_minutes, SCHOOL_TYPE_CODES, DEFAULT_SEARCH_RADIUS

router = APIRouter()


# =============================================================================
# 物件の最寄駅を自動設定
# =============================================================================

@router.post("/properties/{property_id}/set-nearest-stations")
async def set_property_nearest_stations(
    property_id: int,
    limit: int = Query(3, description="設定する駅数", ge=1, le=5)
):
    """
    物件の緯度経度から最寄駅を自動検索し、transportation JSONに設定
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # 物件の緯度経度を取得
        cur.execute("""
            SELECT latitude, longitude FROM properties WHERE id = %s AND deleted_at IS NULL
        """, (property_id,))
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="物件が見つかりません")

        lat, lng = row
        if not lat or not lng:
            raise HTTPException(status_code=400, detail="物件に緯度経度が設定されていません")

        # 最寄駅検索
        cur.execute("""
            SELECT
                station_name,
                line_name,
                ST_Distance(
                    geom::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) as distance_m
            FROM m_stations
            WHERE ST_DWithin(
                geom::geography,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s
            )
            ORDER BY distance_m
            LIMIT %s
        """, (float(lng), float(lat), float(lng), float(lat), DEFAULT_SEARCH_RADIUS['station'], limit))

        stations = cur.fetchall()

        # transportation JSON形式に変換
        transportation = []
        for station_name, line_name, distance_m in stations:
            walk_min = calc_walk_minutes(distance_m)
            transportation.append({
                'station_name': station_name,
                'line_name': line_name or '',
                'walk_minutes': walk_min
            })

        # 物件に保存（transportationカラムがあれば）
        cur.execute("""
            UPDATE properties
            SET transportation = %s
            WHERE id = %s
        """, (json.dumps(transportation), property_id))

        conn.commit()

        return {
            'property_id': property_id,
            'stations_set': len(transportation),
            'transportation': transportation
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


# =============================================================================
# 物件の学区を自動設定
# =============================================================================

@router.post("/properties/{property_id}/set-school-districts")
async def set_property_school_districts(property_id: int):
    """
    物件の緯度経度から学区を自動判定し、保存
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # 物件の緯度経度を取得
        cur.execute("""
            SELECT latitude, longitude FROM properties WHERE id = %s AND deleted_at IS NULL
        """, (property_id,))
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="物件が見つかりません")

        lat, lng = row
        if not lat or not lng:
            raise HTTPException(status_code=400, detail="物件に緯度経度が設定されていません")

        result = {
            'property_id': property_id,
            'elementary_school': None,
            'elementary_school_minutes': None,
            'junior_high_school': None,
            'junior_high_school_minutes': None
        }

        # 小学校区を検索
        cur.execute("""
            SELECT sd.school_name
            FROM m_school_districts sd
            WHERE sd.school_type = '小学校'
            AND ST_Contains(
                sd.area,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
            LIMIT 1
        """, (float(lng), float(lat)))

        row = cur.fetchone()
        if row:
            result['elementary_school'] = row[0]
            # 最寄りの小学校を検索して距離を計算
            cur.execute("""
                SELECT
                    ST_Distance(
                        location::geography,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                    ) as distance_m
                FROM m_schools
                WHERE school_type = %s
                AND ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    %s
                )
                ORDER BY distance_m
                LIMIT 1
            """, (float(lng), float(lat), SCHOOL_TYPE_CODES['elementary'], float(lng), float(lat), DEFAULT_SEARCH_RADIUS['school']))
            dist_row = cur.fetchone()
            if dist_row:
                # 徒歩分数 = 距離(m) / 80m/分
                result['elementary_school_minutes'] = calc_walk_minutes(int(dist_row[0]))

        # 中学校区を検索
        cur.execute("""
            SELECT sd.school_name
            FROM m_school_districts sd
            WHERE sd.school_type = '中学校'
            AND ST_Contains(
                sd.area,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
            LIMIT 1
        """, (float(lng), float(lat)))

        row = cur.fetchone()
        if row:
            result['junior_high_school'] = row[0]
            # 最寄りの中学校を検索して距離を計算
            cur.execute("""
                SELECT
                    ST_Distance(
                        location::geography,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                    ) as distance_m
                FROM m_schools
                WHERE school_type = %s
                AND ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    %s
                )
                ORDER BY distance_m
                LIMIT 1
            """, (float(lng), float(lat), SCHOOL_TYPE_CODES['junior_high'], float(lng), float(lat), DEFAULT_SEARCH_RADIUS['school']))
            dist_row = cur.fetchone()
            if dist_row:
                # 徒歩分数 = 距離(m) / 80m/分
                result['junior_high_school_minutes'] = calc_walk_minutes(int(dist_row[0]))

        # 物件に保存
        cur.execute("""
            UPDATE properties SET
                elementary_school = %s,
                elementary_school_minutes = %s,
                junior_high_school = %s,
                junior_high_school_minutes = %s
            WHERE id = %s
        """, (
            result['elementary_school'],
            result['elementary_school_minutes'],
            result['junior_high_school'],
            result['junior_high_school_minutes'],
            property_id
        ))

        conn.commit()

        return result

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


# =============================================================================
# 物件の用途地域を自動設定
# =============================================================================

@router.post("/properties/{property_id}/set-zoning")
async def set_property_zoning(property_id: int):
    """
    物件の緯度経度から用途地域を自動判定し、保存

    - use_district: 複数の場合はJSON配列形式で保存
    - building_coverage_ratio, floor_area_ratio: 主たる用途地域の値を設定（後で手動変更可能）
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # 物件の緯度経度を取得
        cur.execute("""
            SELECT latitude, longitude FROM properties WHERE id = %s AND deleted_at IS NULL
        """, (property_id,))
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="物件が見つかりません")

        lat, lng = row
        if not lat or not lng:
            raise HTTPException(status_code=400, detail="物件に緯度経度が設定されていません")

        # 用途地域を検索
        cur.execute("""
            SELECT
                zone_code,
                zone_name,
                building_coverage_ratio,
                floor_area_ratio,
                ST_Area(geom::geography) as area_sq_m
            FROM m_zoning
            WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ORDER BY area_sq_m DESC
        """, (float(lng), float(lat)))

        rows = cur.fetchall()

        result = {
            'property_id': property_id,
            'zones': [],
            'use_district': None,
            'building_coverage_ratio': None,
            'floor_area_ratio': None
        }

        if rows:
            # 全ての用途地域を記録
            zone_codes = []
            for i, row in enumerate(rows):
                zone_code, zone_name, bcr, far, _ = row
                zone_codes.append(str(zone_code))
                result['zones'].append({
                    'zone_code': zone_code,
                    'zone_name': zone_name,
                    'building_coverage_ratio': bcr,
                    'floor_area_ratio': far,
                    'is_primary': (i == 0)
                })

            # 主たる用途地域（面積最大）の値を設定
            primary = rows[0]
            # JSONB配列形式で保存（master_optionsと形式を統一）
            result['use_district'] = json.dumps([str(primary[0])])
            result['building_coverage_ratio'] = primary[2]
            result['floor_area_ratio'] = primary[3]

        # land_infoテーブルに保存
        cur.execute("""
            UPDATE land_info SET
                use_district = %s,
                building_coverage_ratio = %s,
                floor_area_ratio = %s
            WHERE property_id = %s
        """, (
            result['use_district'],
            result['building_coverage_ratio'],
            result['floor_area_ratio'],
            property_id
        ))

        # 更新された行がない場合、land_infoレコードがないのでINSERT
        if cur.rowcount == 0:
            cur.execute("""
                INSERT INTO land_info (property_id, use_district, building_coverage_ratio, floor_area_ratio)
                VALUES (%s, %s, %s, %s)
            """, (
                property_id,
                result['use_district'],
                result['building_coverage_ratio'],
                result['floor_area_ratio']
            ))

        conn.commit()

        return result

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
