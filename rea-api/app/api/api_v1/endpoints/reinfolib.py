"""
不動産情報ライブラリAPI エンドポイント

国土交通省の不動産情報ライブラリAPIと連携し、
物件の法令制限・ハザード情報を取得

メタデータ駆動: api_aliasesを使用してAPI返却値→DBコードに変換
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import logging

from app.services.reinfolib import ReinfLibClient
from app.core.database import get_connection

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_code_mapping(category_code: str) -> Dict[str, str]:
    """
    マスタオプションからapi_aliases→option_codeのマッピングを取得
    メタデータ駆動: DBのapi_aliasesを使用
    """
    mapping = {}
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT mo.option_code, mo.api_aliases
            FROM master_options mo
            JOIN master_categories mc ON mo.category_id = mc.id
            WHERE mc.category_code = %s
              AND mo.api_aliases IS NOT NULL
              AND mo.deleted_at IS NULL
        ''', (category_code,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        for option_code, aliases in rows:
            if aliases:
                for alias in aliases:
                    mapping[alias] = option_code
    except Exception as e:
        logger.error(f"Failed to get code mapping for {category_code}: {e}")

    return mapping


def _convert_to_codes(regulations: Dict[str, Any]) -> Dict[str, Any]:
    """
    規制情報の日本語名をDBコードに変換
    メタデータ駆動: api_aliasesマッピングを使用
    """
    codes = {}

    # 用途地域
    if regulations.get('use_area') and regulations['use_area'].get('用途地域'):
        zoning_map = _get_code_mapping('zoning_district')
        zone_name = regulations['use_area']['用途地域']
        codes['use_district'] = zoning_map.get(zone_name)

    # 建ぺい率・容積率（数値変換）
    if regulations.get('use_area'):
        coverage = regulations['use_area'].get('建ぺい率', '')
        if coverage:
            try:
                codes['building_coverage_ratio'] = float(coverage.replace('%', ''))
            except ValueError:
                pass

        floor = regulations['use_area'].get('容積率', '')
        if floor:
            try:
                codes['floor_area_ratio'] = float(floor.replace('%', ''))
            except ValueError:
                pass

    # 防火地域
    if regulations.get('fire_prevention') and regulations['fire_prevention'].get('防火地域区分'):
        fire_map = _get_code_mapping('fire_prevention')
        fire_name = regulations['fire_prevention']['防火地域区分']
        codes['fire_prevention_area'] = fire_map.get(fire_name)

    # 地区計画名
    if regulations.get('district_plan') and regulations['district_plan'].get('地区計画名'):
        codes['district_plan_name'] = regulations['district_plan']['地区計画名']

    return codes


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

    メタデータ駆動: codesフィールドにDBコード変換済みの値を返す
    """
    try:
        client = ReinfLibClient()
        results = client.get_all_regulations(lat, lng)

        # メタデータ駆動: API値→DBコードに変換
        codes = _convert_to_codes(results)

        return {
            "status": "success",
            "coordinates": {"lat": lat, "lng": lng},
            "regulations": results,
            "codes": codes  # フロントエンドはこれを使ってsetValue
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
    lng: float = Query(..., description="経度"),
    radius: int = Query(1, description="取得範囲（1=3x3タイル, 2=5x5タイル）")
):
    """
    指定APIのタイルデータ（GeoJSON）を取得

    MAP表示用の生データを返す（周辺タイルも含む広域取得）
    """
    try:
        client = ReinfLibClient()
        available = client.get_available_apis()

        if api_code not in available:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid API code. Available: {list(available.keys())}"
            )

        # 広域取得（3x3または5x5タイル）
        geojson = client.get_tile_data_wide(api_code, lat, lng, radius=radius)
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
