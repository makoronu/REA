"""
地理情報API

- 最寄駅検索
- 住所→緯度経度変換（Geocoding）
- 用途地域判定
- 学区判定
- 周辺施設検索
"""

import logging
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
import urllib.request
import urllib.parse
import json
import sys
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parents[5]))
from shared.database import READatabase
from shared.constants import calc_walk_minutes, SCHOOL_TYPE_CODES, DEFAULT_SEARCH_RADIUS

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


class SchoolCandidate(BaseModel):
    school_name: str
    address: Optional[str]
    admin_type: Optional[str]  # "公立", "私立" etc
    distance_meters: int
    walk_minutes: int
    is_in_district: bool  # 学区ポリゴン内かどうか


class SchoolDistrictsResponse(BaseModel):
    elementary: list[SchoolCandidate]  # 小学校候補リスト（距離順、最大10件）
    junior_high: list[SchoolCandidate]  # 中学校候補リスト（距離順、最大10件）
    latitude: float
    longitude: float


class BusStopCandidate(BaseModel):
    name: str
    bus_type: Optional[str]  # "民間路線バス", "公営路線バス", etc
    operators: list[str]  # 事業者名リスト
    routes: list[str]  # バス路線名リスト
    distance_meters: int
    walk_minutes: int


class NearestBusStopsResponse(BaseModel):
    bus_stops: list[BusStopCandidate]
    latitude: float
    longitude: float


class FacilityCandidate(BaseModel):
    id: int
    name: str
    category_code: str  # "hospital", "clinic", "park", "post_office"
    category_name: str  # 日本語カテゴリ名
    address: Optional[str]
    distance_meters: int
    walk_minutes: int


class NearestFacilitiesResponse(BaseModel):
    facilities: list[FacilityCandidate]
    latitude: float
    longitude: float


class ZoningCandidate(BaseModel):
    zone_code: int  # 用途地域コード（1-12, 21, 99）
    zone_name: str  # 用途地域名
    building_coverage_ratio: Optional[int]  # 建ぺい率（%）
    floor_area_ratio: Optional[int]  # 容積率（%）
    city_name: Optional[str]  # 市区町村名
    is_primary: bool  # 主たる用途地域かどうか（面積最大）


class ZoningResponse(BaseModel):
    zones: list[ZoningCandidate]  # 複数の用途地域（跨っている場合）
    latitude: float
    longitude: float


class UrbanPlanningCandidate(BaseModel):
    layer_no: int  # 都市計画区分コード（1-4）
    area_type: str  # 区分名（市街化区域、市街化調整区域等）
    is_primary: bool  # 主たる区分かどうか


class UrbanPlanningResponse(BaseModel):
    areas: list[UrbanPlanningCandidate]
    latitude: float
    longitude: float


# カテゴリ情報はDBから動的取得（m_facility_categories テーブル）
def get_facility_categories():
    """DBからカテゴリ一覧を取得（display_order >= 0 のみ）"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT category_code, category_name, icon
            FROM m_facility_categories
            WHERE display_order >= 0
            ORDER BY display_order, id
        """)
        return {row[0]: {'name': row[1], 'icon': row[2]} for row in cur.fetchall()}
    finally:
        cur.close()
        conn.close()


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
            walk_min = calc_walk_minutes(distance_m)
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
    """
    try:
        encoded_address = urllib.parse.quote(address)
        url = f"{settings.GSI_GEOCODE_URL}?q={encoded_address}"

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
        logger.error(f"GSI Geocoding error: {e}")

    return None


def geocode_nominatim(address: str) -> Optional[dict]:
    """
    OpenStreetMap Nominatim（無料・利用制限あり）
    フォールバック用
    """
    try:
        encoded_address = urllib.parse.quote(address)
        url = f"{settings.NOMINATIM_GEOCODE_URL}?q={encoded_address}&format=json&limit=1&countrycodes=jp"

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
        logger.error(f"Nominatim Geocoding error: {e}")

    return None


def get_google_api_key() -> Optional[str]:
    """
    Google Maps APIキーを取得
    DB設定 > 環境変数 の優先順位
    """
    # DBから取得を試みる
    try:
        db = READatabase()
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT value FROM system_settings WHERE key = 'GOOGLE_MAPS_API_KEY'")
            row = cur.fetchone()
            if row and row[0]:
                return row[0]
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        logger.debug(f"DB設定取得エラー（フォールバック使用）: {e}")

    # 環境変数にフォールバック
    return settings.GOOGLE_MAPS_API_KEY


def geocode_google(address: str) -> Optional[dict]:
    """
    Google Maps Geocoding API（有料・高精度）
    優先使用
    """
    api_key = get_google_api_key()
    if not api_key:
        logger.debug("GOOGLE_MAPS_API_KEY not set, skipping Google Geocoding")
        return None

    try:
        encoded_address = urllib.parse.quote(address)
        url = f"{settings.GOOGLE_GEOCODE_URL}?address={encoded_address}&key={api_key}&language=ja&region=jp"

        req = urllib.request.Request(url, headers={'User-Agent': 'REA/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data.get('status') == 'OK' and data.get('results'):
            result = data['results'][0]
            location = result.get('geometry', {}).get('location', {})
            if location.get('lat') and location.get('lng'):
                return {
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'address': result.get('formatted_address', address),
                    'source': 'google'
                }
        elif data.get('status') == 'ZERO_RESULTS':
            logger.debug(f"Google Geocoding: no results for '{address}'")
        else:
            logger.warning(f"Google Geocoding status: {data.get('status')}")

    except Exception as e:
        logger.error(f"Google Geocoding error: {e}")

    return None


@router.get("/geocode", response_model=GeocodeResponse)
async def geocode_address(
    address: str = Query(..., description="住所", min_length=3)
):
    """
    住所から緯度経度を取得

    1. Google Maps API（高精度・有料）
    2. 国土地理院API（無料）
    3. Nominatim（OSM・無料）
    """
    # 1. Google Maps API（APIキー設定時のみ）
    result = geocode_google(address)
    if result:
        return GeocodeResponse(**result)

    # 2. 国土地理院API
    result = geocode_gsi(address)
    if result:
        return GeocodeResponse(**result)

    # 3. Nominatimフォールバック
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
    lng: float = Query(..., description="経度", ge=-180, le=180),
    limit: int = Query(10, description="最大取得件数", ge=1, le=20)
):
    """
    指定座標から小学校・中学校の候補を取得

    - 距離順に最大10件を返す
    - 学区ポリゴン内の学校は is_in_district=true
    - 学区ポリゴンがない地域でも最寄りの学校を返す
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # 学区ポリゴン内の学校名を取得
        cur.execute("""
            SELECT school_name FROM m_school_districts
            WHERE school_type = '小学校'
            AND ST_Contains(area, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        """, (lng, lat))
        elementary_district_names = set(row[0] for row in cur.fetchall())

        cur.execute("""
            SELECT school_name FROM m_school_districts
            WHERE school_type = '中学校'
            AND ST_Contains(area, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        """, (lng, lat))
        junior_high_district_names = set(row[0] for row in cur.fetchall())

        # 小学校候補を取得（距離順、上限なし距離）
        cur.execute("""
            SELECT
                name,
                address,
                admin_type_name,
                ST_Distance(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) as distance_m
            FROM m_schools
            WHERE school_type = %s
            ORDER BY distance_m
            LIMIT %s
        """, (lng, lat, SCHOOL_TYPE_CODES['elementary'], limit))

        elementary_candidates = []
        for row in cur.fetchall():
            name, address, admin_type, distance_m = row
            distance_m = int(distance_m)
            walk_min = calc_walk_minutes(distance_m)
            is_in_district = name in elementary_district_names
            elementary_candidates.append(SchoolCandidate(
                school_name=name,
                address=address,
                admin_type=admin_type,
                distance_meters=distance_m,
                walk_minutes=walk_min,
                is_in_district=is_in_district
            ))

        # 中学校候補を取得（距離順、上限なし距離）
        cur.execute("""
            SELECT
                name,
                address,
                admin_type_name,
                ST_Distance(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) as distance_m
            FROM m_schools
            WHERE school_type = %s
            ORDER BY distance_m
            LIMIT %s
        """, (lng, lat, SCHOOL_TYPE_CODES['junior_high'], limit))

        junior_high_candidates = []
        for row in cur.fetchall():
            name, address, admin_type, distance_m = row
            distance_m = int(distance_m)
            walk_min = calc_walk_minutes(distance_m)
            is_in_district = name in junior_high_district_names
            junior_high_candidates.append(SchoolCandidate(
                school_name=name,
                address=address,
                admin_type=admin_type,
                distance_meters=distance_m,
                walk_minutes=walk_min,
                is_in_district=is_in_district
            ))

        # 学区内の学校を先頭に並び替え（距離順は維持しつつ）
        elementary_candidates.sort(key=lambda x: (not x.is_in_district, x.distance_meters))
        junior_high_candidates.sort(key=lambda x: (not x.is_in_district, x.distance_meters))

        return SchoolDistrictsResponse(
            elementary=elementary_candidates,
            junior_high=junior_high_candidates,
            latitude=lat,
            longitude=lng
        )

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
# 最寄りバス停検索
# =============================================================================

@router.get("/nearest-bus-stops", response_model=NearestBusStopsResponse)
async def get_nearest_bus_stops(
    lat: float = Query(..., description="緯度", ge=-90, le=90),
    lng: float = Query(..., description="経度", ge=-180, le=180),
    limit: int = Query(10, description="最大取得件数", ge=1, le=20)
):
    """
    指定座標から最寄りのバス停を検索

    - 距離順に最大10件を返す
    - 事業者名・路線名を含む
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                name,
                bus_type_name,
                operators,
                bus_routes,
                ST_Distance(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) as distance_m
            FROM m_bus_stops
            ORDER BY distance_m
            LIMIT %s
        """, (lng, lat, limit))

        bus_stops = []
        for row in cur.fetchall():
            name, bus_type, operators, routes, distance_m = row
            distance_m = int(distance_m)
            walk_min = calc_walk_minutes(distance_m)
            bus_stops.append(BusStopCandidate(
                name=name,
                bus_type=bus_type,
                operators=operators or [],
                routes=routes or [],
                distance_meters=distance_m,
                walk_minutes=walk_min
            ))

        return NearestBusStopsResponse(
            bus_stops=bus_stops,
            latitude=lat,
            longitude=lng
        )

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
# 最寄り施設検索
# =============================================================================

@router.get("/nearest-facilities", response_model=NearestFacilitiesResponse)
async def get_nearest_facilities(
    lat: float = Query(..., description="緯度", ge=-90, le=90),
    lng: float = Query(..., description="経度", ge=-180, le=180),
    category: Optional[str] = Query(None, description="カテゴリ（hospital, clinic, park, post_office）"),
    limit: int = Query(10, description="最大取得件数", ge=1, le=50)
):
    """
    指定座標から最寄りの施設を検索

    - category指定なし: 全カテゴリから検索
    - category指定あり: 指定カテゴリのみ検索
    - 距離順に返す
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # カテゴリフィルタ
        category_filter = ""
        params = [lng, lat]
        if category:
            category_filter = "AND category_code = %s"
            params.append(category)
        params.append(limit)

        cur.execute("""
            SELECT
                id,
                name,
                category_code,
                address,
                ST_Distance(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                ) as distance_m
            FROM m_facilities
            WHERE location IS NOT NULL
            {}
            ORDER BY distance_m
            LIMIT %s
        """.format(category_filter), params)

        categories = get_facility_categories()
        facilities = []
        for row in cur.fetchall():
            fac_id, name, cat_code, address, distance_m = row
            distance_m = int(distance_m)
            walk_min = calc_walk_minutes(distance_m)
            facilities.append(FacilityCandidate(
                id=fac_id,
                name=name,
                category_code=cat_code,
                category_name=categories.get(cat_code, {}).get('name', cat_code),
                address=address,
                distance_meters=distance_m,
                walk_minutes=walk_min
            ))

        return NearestFacilitiesResponse(
            facilities=facilities,
            latitude=lat,
            longitude=lng
        )

    finally:
        cur.close()
        conn.close()


@router.get("/nearest-facilities-by-category")
async def get_nearest_facilities_by_category(
    lat: float = Query(..., description="緯度", ge=-90, le=90),
    lng: float = Query(..., description="経度", ge=-180, le=180),
    limit_per_category: int = Query(3, description="カテゴリごとの取得件数", ge=1, le=10)
):
    """
    指定座標から各カテゴリごとに最寄りの施設を検索

    - 病院、診療所、公園、郵便局ごとに指定件数ずつ返す
    - 物件編集画面での「周辺施設」表示用
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # DBからカテゴリ一覧を取得
        categories = get_facility_categories()
        result = {}

        for cat_code, cat_info in categories.items():
            cur.execute("""
                SELECT
                    id,
                    name,
                    address,
                    ST_Distance(
                        location::geography,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                    ) as distance_m
                FROM m_facilities
                WHERE location IS NOT NULL
                AND category_code = %s
                ORDER BY distance_m
                LIMIT %s
            """, (lng, lat, cat_code, limit_per_category))

            facilities = []
            for row in cur.fetchall():
                fac_id, name, address, distance_m = row
                distance_m = int(distance_m)
                walk_min = calc_walk_minutes(distance_m)
                facilities.append({
                    'id': fac_id,
                    'name': name,
                    'address': address,
                    'distance_meters': distance_m,
                    'walk_minutes': walk_min
                })

            # 施設がある場合のみ結果に含める
            if facilities:
                result[cat_code] = {
                    'category_name': cat_info['name'],
                    'icon': cat_info['icon'],
                    'facilities': facilities
                }

        return {
            'latitude': lat,
            'longitude': lng,
            'categories': result
        }

    finally:
        cur.close()
        conn.close()


# =============================================================================
# 用途地域判定
# =============================================================================

@router.get("/zoning", response_model=ZoningResponse)
async def get_zoning(
    lat: float = Query(..., description="緯度", ge=-90, le=90),
    lng: float = Query(..., description="経度", ge=-180, le=180)
):
    """
    指定座標の用途地域を判定

    - 座標が複数の用途地域にまたがる場合、すべて返す
    - is_primary=true が主たる用途地域（面積最大）
    - 建ぺい率・容積率も含めて返す
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # 座標を含む用途地域ポリゴンを検索
        # 面積が小さい順（より詳細なポリゴンを優先）
        cur.execute("""
            SELECT
                zone_code,
                zone_name,
                building_coverage_ratio,
                floor_area_ratio,
                city_name,
                ST_Area(geom::geography) as area_sq_m
            FROM m_zoning
            WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ORDER BY area_sq_m DESC
        """, (lng, lat))

        rows = cur.fetchall()

        zones = []
        for i, row in enumerate(rows):
            zone_code, zone_name, bcr, far, city_name, _ = row
            zones.append(ZoningCandidate(
                zone_code=zone_code,
                zone_name=zone_name,
                building_coverage_ratio=bcr,
                floor_area_ratio=far,
                city_name=city_name,
                is_primary=(i == 0)  # 面積最大が主たる用途地域
            ))

        return ZoningResponse(
            zones=zones,
            latitude=lat,
            longitude=lng
        )

    finally:
        cur.close()
        conn.close()


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
            # TODO: m_zoningのzone_codeをmaster_optionsのrea_Xコードにマッピング
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


# =============================================================================
# 用途地域ポリゴン取得（地図表示用）
# =============================================================================

@router.get("/zoning/geojson")
async def get_zoning_geojson(
    min_lat: float = Query(..., description="最小緯度"),
    min_lng: float = Query(..., description="最小経度"),
    max_lat: float = Query(..., description="最大緯度"),
    max_lng: float = Query(..., description="最大経度"),
    simplify: float = Query(0.0001, description="ポリゴン簡略化の許容誤差（度）")
):
    """
    指定範囲内の用途地域ポリゴンをGeoJSON形式で返す

    - 地図表示用
    - simplifyで精度を落としてデータ量削減
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # バウンディングボックスでフィルタ
        cur.execute("""
            SELECT
                id,
                zone_code,
                zone_name,
                building_coverage_ratio,
                floor_area_ratio,
                city_name,
                ST_AsGeoJSON(ST_Simplify(geom, %s)) as geojson
            FROM m_zoning
            WHERE geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
            LIMIT 5000
        """, (simplify, min_lng, min_lat, max_lng, max_lat))

        features = []
        for row in cur.fetchall():
            zoning_id, zone_code, zone_name, bcr, far, city_name, geojson_str = row
            if geojson_str:
                import json
                geometry = json.loads(geojson_str)
                features.append({
                    "type": "Feature",
                    "properties": {
                        "id": zoning_id,
                        "zone_code": zone_code,
                        "zone_name": zone_name,
                        "building_coverage_ratio": bcr,
                        "floor_area_ratio": far,
                        "city_name": city_name
                    },
                    "geometry": geometry
                })

        return {
            "type": "FeatureCollection",
            "features": features
        }

    finally:
        cur.close()
        conn.close()


@router.get("/zoning/legend")
async def get_zoning_legend():
    """
    用途地域の凡例（色とラベル）を返す
    """
    # 用途地域コードと色のマッピング（都市計画法に基づく標準色）
    legend = [
        {"code": 1, "name": "第一種低層住居専用地域", "color": "#00FF00", "description": "低層住宅の良好な環境を保護"},
        {"code": 2, "name": "第二種低層住居専用地域", "color": "#80FF00", "description": "小規模店舗も許容"},
        {"code": 3, "name": "第一種中高層住居専用地域", "color": "#FFFF00", "description": "中高層住宅の良好な環境"},
        {"code": 4, "name": "第二種中高層住居専用地域", "color": "#FFCC00", "description": "必要な利便施設も許容"},
        {"code": 5, "name": "第一種住居地域", "color": "#FF9900", "description": "住居の環境を保護"},
        {"code": 6, "name": "第二種住居地域", "color": "#FF6600", "description": "主に住居の環境を保護"},
        {"code": 7, "name": "準住居地域", "color": "#FF3300", "description": "道路沿道の業務利便と住居の調和"},
        {"code": 8, "name": "近隣商業地域", "color": "#FF00FF", "description": "近隣住民の日用品供給"},
        {"code": 9, "name": "商業地域", "color": "#FF0000", "description": "商業等の業務の利便増進"},
        {"code": 10, "name": "準工業地域", "color": "#00FFFF", "description": "環境悪化の恐れのない工業"},
        {"code": 11, "name": "工業地域", "color": "#0080FF", "description": "工業の利便増進"},
        {"code": 12, "name": "工業専用地域", "color": "#0000FF", "description": "工業の利便増進（住宅不可）"},
        {"code": 21, "name": "田園住居地域", "color": "#90EE90", "description": "農業と調和した低層住宅"},
        {"code": 99, "name": "無指定", "color": "#CCCCCC", "description": "用途地域の指定なし"}
    ]
    return legend


# =============================================================================
# 都市計画区域判定
# =============================================================================

@router.get("/urban-planning", response_model=UrbanPlanningResponse)
async def get_urban_planning(
    lat: float = Query(..., description="緯度", ge=-90, le=90),
    lng: float = Query(..., description="経度", ge=-180, le=180)
):
    """
    指定座標の都市計画区域を判定

    - layer_no: 1=市街化区域, 2=市街化調整区域, 3=その他用途地域, 4=用途未設定
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # 面積が小さい順（より詳細なポリゴンを優先）
        # 市街化区域(1)を市街化調整区域(2)より優先するため、layer_noでもソート
        cur.execute("""
            SELECT
                layer_no,
                area_type,
                ST_Area(geom::geography) as area_sq_m
            FROM m_urban_planning
            WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ORDER BY layer_no ASC, area_sq_m ASC
        """, (lng, lat))

        rows = cur.fetchall()

        areas = []
        for i, row in enumerate(rows):
            layer_no, area_type, _ = row
            areas.append(UrbanPlanningCandidate(
                layer_no=layer_no,
                area_type=area_type,
                is_primary=(i == 0)
            ))

        return UrbanPlanningResponse(
            areas=areas,
            latitude=lat,
            longitude=lng
        )

    finally:
        cur.close()
        conn.close()


@router.get("/urban-planning/geojson")
async def get_urban_planning_geojson(
    min_lat: float = Query(..., description="最小緯度"),
    min_lng: float = Query(..., description="最小経度"),
    max_lat: float = Query(..., description="最大緯度"),
    max_lng: float = Query(..., description="最大経度"),
    simplify: float = Query(0.0001, description="ポリゴン簡略化の許容誤差（度）")
):
    """
    指定範囲内の都市計画区域ポリゴンをGeoJSON形式で返す
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                id,
                layer_no,
                area_type,
                ST_AsGeoJSON(ST_Simplify(geom, %s)) as geojson
            FROM m_urban_planning
            WHERE geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
            LIMIT 3000
        """, (simplify, min_lng, min_lat, max_lng, max_lat))

        features = []
        for row in cur.fetchall():
            plan_id, layer_no, area_type, geojson_str = row
            if geojson_str:
                import json
                geometry = json.loads(geojson_str)
                features.append({
                    "type": "Feature",
                    "properties": {
                        "id": plan_id,
                        "layer_no": layer_no,
                        "area_type": area_type
                    },
                    "geometry": geometry
                })

        return {
            "type": "FeatureCollection",
            "features": features
        }

    finally:
        cur.close()
        conn.close()
