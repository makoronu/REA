"""
不動産情報ライブラリAPI エンドポイント

国土交通省の不動産情報ライブラリAPIと連携し、
物件の法令制限・ハザード情報を取得
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from app.services.reinfolib import ReinfLibClient

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/regulations")
async def get_regulations(
    lat: float = Query(..., description="緯度"),
    lng: float = Query(..., description="経度")
):
    """
    指定座標の全規制情報を取得

    - 用途地域
    - 防火・準防火地域
    - 洪水浸水想定区域
    - 土砂災害警戒区域
    - 津波浸水想定
    - 高潮浸水想定区域
    - 立地適正化計画
    - 地区計画
    - 都市計画道路
    """
    try:
        client = ReinfLibClient()
        results = client.get_all_regulations(lat, lng)
        return {
            "status": "success",
            "coordinates": {"lat": lat, "lng": lng},
            "regulations": results
        }
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get regulations: {e}")
        raise HTTPException(status_code=500, detail="規制情報の取得に失敗しました")


@router.get("/use-area")
async def get_use_area(
    lat: float = Query(..., description="緯度"),
    lng: float = Query(..., description="経度")
):
    """用途地域を取得"""
    try:
        client = ReinfLibClient()
        result = client.get_regulation_at_point("XKT002", lat, lng)
        if result:
            return {
                "status": "success",
                "data": client._map_properties("XKT002", result)
            }
        return {"status": "success", "data": None, "message": "該当なし"}
    except Exception as e:
        logger.error(f"Failed to get use area: {e}")
        raise HTTPException(status_code=500, detail="用途地域の取得に失敗しました")


@router.get("/hazard")
async def get_hazard_info(
    lat: float = Query(..., description="緯度"),
    lng: float = Query(..., description="経度")
):
    """
    ハザード情報を取得

    - 洪水浸水想定区域
    - 土砂災害警戒区域
    - 津波浸水想定
    - 高潮浸水想定区域
    """
    try:
        client = ReinfLibClient()
        results = {}

        # 洪水
        props = client.get_regulation_at_point("XKT026", lat, lng)
        results["flood"] = client._map_properties("XKT026", props) if props else None

        # 土砂災害
        props = client.get_regulation_at_point("XKT029", lat, lng)
        results["landslide"] = client._map_properties("XKT029", props) if props else None

        # 津波
        props = client.get_regulation_at_point("XKT028", lat, lng)
        results["tsunami"] = client._map_properties("XKT028", props) if props else None

        # 高潮
        props = client.get_regulation_at_point("XKT027", lat, lng)
        results["storm_surge"] = client._map_properties("XKT027", props) if props else None

        # リスクありかどうかを判定
        has_risk = any(v is not None for v in results.values())

        return {
            "status": "success",
            "has_risk": has_risk,
            "data": results
        }
    except Exception as e:
        logger.error(f"Failed to get hazard info: {e}")
        raise HTTPException(status_code=500, detail="ハザード情報の取得に失敗しました")


@router.get("/tile/{api_code}")
async def get_tile_geojson(
    api_code: str,
    lat: float = Query(..., description="緯度"),
    lng: float = Query(..., description="経度")
):
    """
    指定APIのタイルデータ（GeoJSON）を取得

    MAP表示用の生データを返す
    """
    try:
        client = ReinfLibClient()
        available = client.get_available_apis()

        if api_code not in available:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid API code. Available: {list(available.keys())}"
            )

        geojson = client.get_tile_data(api_code, lat, lng)
        return geojson

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tile data: {e}")
        raise HTTPException(status_code=500, detail="タイルデータの取得に失敗しました")


@router.get("/price")
async def get_price_info(
    year: int = Query(..., description="年"),
    area: str = Query(..., description="都道府県コード（01=北海道）"),
    city: Optional[str] = Query(None, description="市区町村コード")
):
    """価格情報を取得"""
    try:
        client = ReinfLibClient()
        result = client.get_price_info(year, area, city)
        return result
    except Exception as e:
        logger.error(f"Failed to get price info: {e}")
        raise HTTPException(status_code=500, detail="価格情報の取得に失敗しました")


@router.get("/apis")
async def get_available_apis():
    """利用可能なAPI一覧"""
    return ReinfLibClient.get_available_apis()
