"""
地理情報API（読み取り専用）

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

from app.config import settings

logger = logging.getLogger(__name__)

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
    walk_minutes: int


class NearestStationsResponse(BaseModel):
    stations: list[NearestStationResponse]
    latitude: float
    longitude: float


class GeocodeResponse(BaseModel):
    address: str
    latitude: float
    longitude: float
    source: str


class SchoolCandidate(BaseModel):
    school_name: str
    address: Optional[str]
    admin_type: Optional[str]
    distance_meters: int
    walk_minutes: int
    is_in_district: bool


class SchoolDistrictsResponse(BaseModel):
    elementary: list[SchoolCandidate]
    junior_high: list[SchoolCandidate]
    latitude: float
    longitude: float


class BusStopCandidate(BaseModel):
    name: str
    bus_type: Optional[str]
    operators: list[str]
    routes: list[str]
    distance_meters: int
    walk_minutes: int


class NearestBusStopsResponse(BaseModel):
    bus_stops: list[BusStopCandidate]
    latitude: float
    longitude: float


class FacilityCandidate(BaseModel):
    id: int
    name: str
    category_code: str
    category_name: str
    address: Optional[str]
    distance_meters: int
    walk_minutes: int


class NearestFacilitiesResponse(BaseModel):
    facilities: list[FacilityCandidate]
    latitude: float
    longitude: float


class ZoningCandidate(BaseModel):
    zone_code: int
    zone_name: str
    building_coverage_ratio: Optional[int]
    floor_area_ratio: Optional[int]
    city_name: Optional[str]
    is_primary: bool


class ZoningResponse(BaseModel):
    zones: list[ZoningCandidate]
    latitude: float
    longitude: float


class UrbanPlanningCandidate(BaseModel):
    layer_no: int
    area_type: str
    is_primary: bool


class UrbanPlanningResponse(BaseModel):
    areas: list[UrbanPlanningCandidate]
    latitude: float
    longitude: float


# =============================================================================
# ヘルパー関数
# =============================================================================

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


def geocode_gsi(address: str) -> Optional[dict]:
    """国土地理院API（無料・制限なし）"""
    try:
        encoded_address = urllib.parse.quote(address)
        url = f"{settings.GSI_GEOCODE_URL}?q={encoded_address}"

        req = urllib.request.Request(url, headers={'User-Agent': 'REA/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data and len(data) > 0:
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
    """OpenStreetMap Nominatim（無料・利用制限あり）"""
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
    """Google Maps APIキーを取得（DB設定 > 環境変数）"""
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

    return settings.GOOGLE_MAPS_API_KEY


def geocode_google(address: str) -> Optional[dict]:
    """Google Maps Geocoding API（有料・高精度）"""
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
    """指定座標から最寄りの駅を検索"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                id, station_name, line_name, company_name,
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

        stations = []
        for row in cur.fetchall():
            distance_m = int(row[4])
            stations.append(NearestStationResponse(
                station_id=row[0],
                station_name=row[1],
                line_name=row[2],
                company_name=row[3],
                distance_meters=distance_m,
                walk_minutes=calc_walk_minutes(distance_m)
            ))

        return NearestStationsResponse(stations=stations, latitude=lat, longitude=lng)

    finally:
        cur.close()
        conn.close()


# =============================================================================
# Geocoding（住所→緯度経度変換）
# =============================================================================

@router.get("/geocode", response_model=GeocodeResponse)
async def geocode_address(
    address: str = Query(..., description="住所", min_length=3)
):
    """住所から緯度経度を取得（Google > GSI > Nominatim）"""
    result = geocode_google(address)
    if result:
        return GeocodeResponse(**result)

    result = geocode_gsi(address)
    if result:
        return GeocodeResponse(**result)

    result = geocode_nominatim(address)
    if result:
        return GeocodeResponse(**result)

    raise HTTPException(
        status_code=404,
        detail="住所から座標を取得できませんでした: {}".format(address)
    )


# =============================================================================
# 学区判定
# =============================================================================

@router.get("/school-districts", response_model=SchoolDistrictsResponse)
async def get_school_districts(
    lat: float = Query(..., description="緯度", ge=-90, le=90),
    lng: float = Query(..., description="経度", ge=-180, le=180),
    limit: int = Query(10, description="最大取得件数", ge=1, le=20)
):
    """指定座標から小学校・中学校の候補を取得"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
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

        cur.execute("""
            SELECT name, address, admin_type_name,
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
            elementary_candidates.append(SchoolCandidate(
                school_name=name, address=address, admin_type=admin_type,
                distance_meters=distance_m,
                walk_minutes=calc_walk_minutes(distance_m),
                is_in_district=name in elementary_district_names
            ))

        cur.execute("""
            SELECT name, address, admin_type_name,
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
            junior_high_candidates.append(SchoolCandidate(
                school_name=name, address=address, admin_type=admin_type,
                distance_meters=distance_m,
                walk_minutes=calc_walk_minutes(distance_m),
                is_in_district=name in junior_high_district_names
            ))

        elementary_candidates.sort(key=lambda x: (not x.is_in_district, x.distance_meters))
        junior_high_candidates.sort(key=lambda x: (not x.is_in_district, x.distance_meters))

        return SchoolDistrictsResponse(
            elementary=elementary_candidates,
            junior_high=junior_high_candidates,
            latitude=lat, longitude=lng
        )

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
    """指定座標から最寄りのバス停を検索"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                name, bus_type_name, operators, bus_routes,
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
            bus_stops.append(BusStopCandidate(
                name=name, bus_type=bus_type,
                operators=operators or [], routes=routes or [],
                distance_meters=distance_m,
                walk_minutes=calc_walk_minutes(distance_m)
            ))

        return NearestBusStopsResponse(bus_stops=bus_stops, latitude=lat, longitude=lng)

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
    category: Optional[str] = Query(None, description="カテゴリコード"),
    limit: int = Query(10, description="最大取得件数", ge=1, le=50)
):
    """指定座標から最寄りの施設を検索"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        category_filter = ""
        params = [lng, lat]
        if category:
            category_filter = "AND category_code = %s"
            params.append(category)
        params.append(limit)

        cur.execute("""
            SELECT
                id, name, category_code, address,
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
            facilities.append(FacilityCandidate(
                id=fac_id, name=name,
                category_code=cat_code,
                category_name=categories.get(cat_code, {}).get('name', cat_code),
                address=address,
                distance_meters=distance_m,
                walk_minutes=calc_walk_minutes(distance_m)
            ))

        return NearestFacilitiesResponse(facilities=facilities, latitude=lat, longitude=lng)

    finally:
        cur.close()
        conn.close()


@router.get("/nearest-facilities-by-category")
async def get_nearest_facilities_by_category(
    lat: float = Query(..., description="緯度", ge=-90, le=90),
    lng: float = Query(..., description="経度", ge=-180, le=180),
    limit_per_category: int = Query(3, description="カテゴリごとの取得件数", ge=1, le=10)
):
    """指定座標から各カテゴリごとに最寄りの施設を検索"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        categories = get_facility_categories()
        result = {}

        for cat_code, cat_info in categories.items():
            cur.execute("""
                SELECT
                    id, name, address,
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
                facilities.append({
                    'id': fac_id, 'name': name, 'address': address,
                    'distance_meters': distance_m,
                    'walk_minutes': calc_walk_minutes(distance_m)
                })

            if facilities:
                result[cat_code] = {
                    'category_name': cat_info['name'],
                    'icon': cat_info['icon'],
                    'facilities': facilities
                }

        return {'latitude': lat, 'longitude': lng, 'categories': result}

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
    """指定座標の用途地域を判定"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                zone_code, zone_name, building_coverage_ratio,
                floor_area_ratio, city_name,
                ST_Area(geom::geography) as area_sq_m
            FROM m_zoning
            WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ORDER BY area_sq_m DESC
        """, (lng, lat))

        zones = []
        for i, row in enumerate(cur.fetchall()):
            zone_code, zone_name, bcr, far, city_name, _ = row
            zones.append(ZoningCandidate(
                zone_code=zone_code, zone_name=zone_name,
                building_coverage_ratio=bcr, floor_area_ratio=far,
                city_name=city_name, is_primary=(i == 0)
            ))

        return ZoningResponse(zones=zones, latitude=lat, longitude=lng)

    finally:
        cur.close()
        conn.close()


@router.get("/zoning/geojson")
async def get_zoning_geojson(
    min_lat: float = Query(..., description="最小緯度"),
    min_lng: float = Query(..., description="最小経度"),
    max_lat: float = Query(..., description="最大緯度"),
    max_lng: float = Query(..., description="最大経度"),
    simplify: float = Query(0.0001, description="ポリゴン簡略化の許容誤差（度）")
):
    """指定範囲内の用途地域ポリゴンをGeoJSON形式で返す"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                id, zone_code, zone_name,
                building_coverage_ratio, floor_area_ratio, city_name,
                ST_AsGeoJSON(ST_Simplify(geom, %s)) as geojson
            FROM m_zoning
            WHERE geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
            LIMIT 5000
        """, (simplify, min_lng, min_lat, max_lng, max_lat))

        features = []
        for row in cur.fetchall():
            zoning_id, zone_code, zone_name, bcr, far, city_name, geojson_str = row
            if geojson_str:
                geometry = json.loads(geojson_str)
                features.append({
                    "type": "Feature",
                    "properties": {
                        "id": zoning_id, "zone_code": zone_code,
                        "zone_name": zone_name,
                        "building_coverage_ratio": bcr,
                        "floor_area_ratio": far, "city_name": city_name
                    },
                    "geometry": geometry
                })

        return {"type": "FeatureCollection", "features": features}

    finally:
        cur.close()
        conn.close()


@router.get("/zoning/legend")
async def get_zoning_legend():
    """用途地域の凡例（色とラベル）を返す"""
    return [
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


# =============================================================================
# 都市計画区域判定
# =============================================================================

@router.get("/urban-planning", response_model=UrbanPlanningResponse)
async def get_urban_planning(
    lat: float = Query(..., description="緯度", ge=-90, le=90),
    lng: float = Query(..., description="経度", ge=-180, le=180)
):
    """指定座標の都市計画区域を判定"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                layer_no, area_type,
                ST_Area(geom::geography) as area_sq_m
            FROM m_urban_planning
            WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            ORDER BY layer_no ASC, area_sq_m ASC
        """, (lng, lat))

        areas = []
        for i, row in enumerate(cur.fetchall()):
            layer_no, area_type, _ = row
            areas.append(UrbanPlanningCandidate(
                layer_no=layer_no, area_type=area_type, is_primary=(i == 0)
            ))

        return UrbanPlanningResponse(areas=areas, latitude=lat, longitude=lng)

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
    """指定範囲内の都市計画区域ポリゴンをGeoJSON形式で返す"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                id, layer_no, area_type,
                ST_AsGeoJSON(ST_Simplify(geom, %s)) as geojson
            FROM m_urban_planning
            WHERE geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
            LIMIT 3000
        """, (simplify, min_lng, min_lat, max_lng, max_lat))

        features = []
        for row in cur.fetchall():
            plan_id, layer_no, area_type, geojson_str = row
            if geojson_str:
                geometry = json.loads(geojson_str)
                features.append({
                    "type": "Feature",
                    "properties": {
                        "id": plan_id, "layer_no": layer_no,
                        "area_type": area_type
                    },
                    "geometry": geometry
                })

        return {"type": "FeatureCollection", "features": features}

    finally:
        cur.close()
        conn.close()
