"""
地理情報API

- 最寄駅検索
- 住所→緯度経度変換（Geocoding）
- 用途地域判定（将来実装）
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
import urllib.request
import urllib.parse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[5]))
from shared.database import READatabase

router = APIRouter()


# =============================================================================
# スキーマ
# =============================================================================

class NearestStationResponse(BaseModel):
    station_id: int
    station_name: str
    line_name: Optional[str]
    company_name: Optional[str]
    distance_meters: int
    walk_minutes: int  # 80m/分で計算


class NearestStationsResponse(BaseModel):
    stations: list[NearestStationResponse]
    latitude: float
    longitude: float


class GeocodeResponse(BaseModel):
    address: str
    latitude: float
    longitude: float
    source: str  # "gsi" or "nominatim"


class SchoolDistrictResponse(BaseModel):
    school_type: str  # "小学校" or "中学校"
    school_name: str
    address: Optional[str]
    admin_type: Optional[str]  # "公立", "私立" etc
    distance_meters: Optional[int]  # 学校までの距離（学校座標がある場合）
    walk_minutes: Optional[int]  # 徒歩分数


class SchoolDistrictsResponse(BaseModel):
    elementary: Optional[SchoolDistrictResponse]
    junior_high: Optional[SchoolDistrictResponse]
    latitude: float
    longitude: float


# =============================================================================
# 最寄駅検索
# =============================================================================

@router.get("/nearest-stations", response_model=NearestStationsResponse)
async def get_nearest_stations(
    lat: float = Query(..., description="緯度", ge=-90, le=90),
    lng: float = Query(..., description="経度", ge=-180, le=180),
    radius: int = Query(2000, description="検索半径（メートル）", ge=100, le=10000),
    limit: int = Query(5, description="取得件数", ge=1, le=20)
):
    """
    指定座標から最寄りの駅を検索

    - radius: 検索半径（デフォルト2km）
    - limit: 最大取得件数（デフォルト5件）
    - 徒歩分数は80m/分で計算
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                id,
                station_name,
                line_name,
                company_name,
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
        """, (lng, lat, lng, lat, radius, limit))

        rows = cur.fetchall()

        stations = []
        for row in rows:
            distance_m = int(row[4])
            walk_min = max(1, round(distance_m / 80))  # 80m/分、最低1分
            stations.append(NearestStationResponse(
                station_id=row[0],
                station_name=row[1],
                line_name=row[2],
                company_name=row[3],
                distance_meters=distance_m,
                walk_minutes=walk_min
            ))

        return NearestStationsResponse(
            stations=stations,
            latitude=lat,
            longitude=lng
        )

    finally:
        cur.close()
        conn.close()


# =============================================================================
# Geocoding（住所→緯度経度変換）
# =============================================================================

def geocode_gsi(address: str) -> Optional[dict]:
    """
    国土地理院API（無料・制限なし）
    https://msearch.gsi.go.jp/address-search/AddressSearch?q=住所
    """
    try:
        encoded_address = urllib.parse.quote(address)
        url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q={}".format(encoded_address)

        req = urllib.request.Request(url, headers={'User-Agent': 'REA/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data and len(data) > 0:
            # 最初の結果を使用
            result = data[0]
            coords = result.get('geometry', {}).get('coordinates', [])
            if len(coords) >= 2:
                return {
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'address': result.get('properties', {}).get('title', address),
                    'source': 'gsi'
                }
    except Exception as e:
        print("GSI Geocoding error: {}".format(e))

    return None


def geocode_nominatim(address: str) -> Optional[dict]:
    """
    OpenStreetMap Nominatim（無料・利用制限あり）
    フォールバック用
    """
    try:
        encoded_address = urllib.parse.quote(address)
        url = "https://nominatim.openstreetmap.org/search?q={}&format=json&limit=1&countrycodes=jp".format(encoded_address)

        req = urllib.request.Request(url, headers={'User-Agent': 'REA/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data and len(data) > 0:
            result = data[0]
            return {
                'latitude': float(result['lat']),
                'longitude': float(result['lon']),
                'address': result.get('display_name', address),
                'source': 'nominatim'
            }
    except Exception as e:
        print("Nominatim Geocoding error: {}".format(e))

    return None


@router.get("/geocode", response_model=GeocodeResponse)
async def geocode_address(
    address: str = Query(..., description="住所", min_length=3)
):
    """
    住所から緯度経度を取得

    1. 国土地理院APIを優先使用（無料・高精度）
    2. 失敗時はNominatim（OSM）をフォールバック
    """
    # 1. 国土地理院API
    result = geocode_gsi(address)
    if result:
        return GeocodeResponse(**result)

    # 2. Nominatimフォールバック
    result = geocode_nominatim(address)
    if result:
        return GeocodeResponse(**result)

    raise HTTPException(
        status_code=404,
        detail="住所から座標を取得できませんでした: {}".format(address)
    )


# =============================================================================
# 学区判定（座標から小中学校区を特定）
# =============================================================================

@router.get("/school-districts", response_model=SchoolDistrictsResponse)
async def get_school_districts(
    lat: float = Query(..., description="緯度", ge=-90, le=90),
    lng: float = Query(..., description="経度", ge=-180, le=180)
):
    """
    指定座標から小学校区・中学校区を判定

    - 座標がポリゴン内に含まれる学区を返す
    - 学校の位置データがある場合は距離も計算
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        result = {
            'elementary': None,
            'junior_high': None,
            'latitude': lat,
            'longitude': lng
        }

        # 小学校区を検索
        cur.execute("""
            SELECT
                sd.school_type,
                sd.school_name,
                sd.address,
                sd.admin_type
            FROM m_school_districts sd
            WHERE sd.school_type = '小学校'
            AND ST_Contains(
                sd.area,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
            LIMIT 1
        """, (lng, lat))

        row = cur.fetchone()
        if row:
            school_type, school_name, address, admin_type = row
            distance_m = None
            walk_min = None

            # 最寄りの小学校を検索して距離を計算
            cur.execute("""
                SELECT
                    ST_Distance(
                        location::geography,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                    ) as distance_m
                FROM m_schools
                WHERE school_type = '16001'
                AND ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    5000
                )
                ORDER BY distance_m
                LIMIT 1
            """, (lng, lat, lng, lat))
            dist_row = cur.fetchone()
            if dist_row:
                distance_m = int(dist_row[0])
                walk_min = max(1, round(distance_m / 80))

            result['elementary'] = SchoolDistrictResponse(
                school_type="小学校",
                school_name=school_name,
                address=address,
                admin_type=admin_type,
                distance_meters=distance_m,
                walk_minutes=walk_min
            )

        # 中学校区を検索
        cur.execute("""
            SELECT
                sd.school_type,
                sd.school_name,
                sd.address,
                sd.admin_type
            FROM m_school_districts sd
            WHERE sd.school_type = '中学校'
            AND ST_Contains(
                sd.area,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
            LIMIT 1
        """, (lng, lat))

        row = cur.fetchone()
        if row:
            school_type, school_name, address, admin_type = row
            distance_m = None
            walk_min = None

            # 最寄りの中学校を検索して距離を計算
            cur.execute("""
                SELECT
                    ST_Distance(
                        location::geography,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                    ) as distance_m
                FROM m_schools
                WHERE school_type = '16002'
                AND ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    5000
                )
                ORDER BY distance_m
                LIMIT 1
            """, (lng, lat, lng, lat))
            dist_row = cur.fetchone()
            if dist_row:
                distance_m = int(dist_row[0])
                walk_min = max(1, round(distance_m / 80))

            result['junior_high'] = SchoolDistrictResponse(
                school_type="中学校",
                school_name=school_name,
                address=address,
                admin_type=admin_type,
                distance_meters=distance_m,
                walk_minutes=walk_min
            )

        return SchoolDistrictsResponse(**result)

    finally:
        cur.close()
        conn.close()


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
            SELECT latitude, longitude FROM properties WHERE id = %s
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
                5000
            )
            ORDER BY distance_m
            LIMIT %s
        """, (float(lng), float(lat), float(lng), float(lat), limit))

        stations = cur.fetchall()

        # transportation JSON形式に変換
        transportation = []
        for station_name, line_name, distance_m in stations:
            walk_min = max(1, round(distance_m / 80))
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
            SELECT latitude, longitude FROM properties WHERE id = %s
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
                WHERE school_type = '16001'
                AND ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    5000
                )
                ORDER BY distance_m
                LIMIT 1
            """, (float(lng), float(lat), float(lng), float(lat)))
            dist_row = cur.fetchone()
            if dist_row:
                # 徒歩分数 = 距離(m) / 80m/分
                result['elementary_school_minutes'] = max(1, round(int(dist_row[0]) / 80))

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
                WHERE school_type = '16002'
                AND ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                    5000
                )
                ORDER BY distance_m
                LIMIT 1
            """, (float(lng), float(lat), float(lng), float(lat)))
            dist_row = cur.fetchone()
            if dist_row:
                # 徒歩分数 = 距離(m) / 80m/分
                result['junior_high_school_minutes'] = max(1, round(int(dist_row[0]) / 80))

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
