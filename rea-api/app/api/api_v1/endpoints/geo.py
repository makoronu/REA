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
            WHERE school_type = '16001'
            ORDER BY distance_m
            LIMIT %s
        """, (lng, lat, limit))

        elementary_candidates = []
        for row in cur.fetchall():
            name, address, admin_type, distance_m = row
            distance_m = int(distance_m)
            walk_min = max(1, round(distance_m / 80))
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
            WHERE school_type = '16002'
            ORDER BY distance_m
            LIMIT %s
        """, (lng, lat, limit))

        junior_high_candidates = []
        for row in cur.fetchall():
            name, address, admin_type, distance_m = row
            distance_m = int(distance_m)
            walk_min = max(1, round(distance_m / 80))
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
            walk_min = max(1, round(distance_m / 80))
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

        facilities = []
        for row in cur.fetchall():
            fac_id, name, cat_code, address, distance_m = row
            distance_m = int(distance_m)
            walk_min = max(1, round(distance_m / 80))
            categories = get_facility_categories()
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
                walk_min = max(1, round(distance_m / 80))
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
