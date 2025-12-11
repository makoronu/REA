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
