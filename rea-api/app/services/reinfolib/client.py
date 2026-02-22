"""
不動産情報ライブラリAPI クライアント

メタデータ駆動設計: API定義は設定で管理、ハードコーディング禁止
"""
import os
import logging
from typing import Optional
import requests
from .tile_utils import lat_lng_to_tile, find_containing_feature
from app.core.config import settings

logger = logging.getLogger(__name__)

# API定義（メタデータ駆動）
API_DEFINITIONS = {
    # 地図タイル系（XYZタイル方式）
    "XKT001": {
        "name": "都市計画区域・区域区分",
        "endpoint": "XKT001",
        "type": "tile",
        "zoom_level": 14,
        "properties_map": {
            "area_classification_ja": "区域区分",
            "prefecture": "都道府県",
            "city_name": "市区町村"
        },
        # kubun_id=21:都市計画区域（広域）, 22:区域区分（市街化/調整/非線引）
        # 22のみ対象にしないと常に「都市計画区域」が返りマッピング不能
        "preferred_kubun_ids": [22],
    },
    "XKT002": {
        "name": "用途地域",
        "endpoint": "XKT002",
        "type": "tile",
        "zoom_level": 14,
        "properties_map": {
            "use_area_ja": "用途地域",
            "u_building_coverage_ratio_ja": "建ぺい率",
            "u_floor_area_ratio_ja": "容積率",
            "prefecture": "都道府県",
            "city_name": "市区町村"
        }
    },
    "XKT014": {
        "name": "防火・準防火地域",
        "endpoint": "XKT014",
        "type": "tile",
        "zoom_level": 14,
        "properties_map": {
            "fire_prevention_ja": "防火地域区分",
            "prefecture": "都道府県",
            "city_name": "市区町村"
        },
        # kubun_id=24:防火地域, 25:準防火地域
        # 境界で両方ヒット時、より厳しい防火地域(24)を優先
        "preferred_kubun_ids": [24, 25],
    },
    "XKT026": {
        "name": "洪水浸水想定区域",
        "endpoint": "XKT026",
        "type": "tile",
        "zoom_level": 14,
        "properties_map": {
            "depth_ja": "浸水深",
            "rank": "浸水ランク",
            "river_name": "河川名"
        }
    },
    "XKT027": {
        "name": "高潮浸水想定区域",
        "endpoint": "XKT027",
        "type": "tile",
        "zoom_level": 14,
        "properties_map": {
            "depth_ja": "浸水深",
            "rank": "浸水ランク"
        }
    },
    "XKT028": {
        "name": "津波浸水想定",
        "endpoint": "XKT028",
        "type": "tile",
        "zoom_level": 14,
        "properties_map": {
            "depth_ja": "浸水深",
            "rank": "浸水ランク"
        }
    },
    "XKT029": {
        "name": "土砂災害警戒区域",
        "endpoint": "XKT029",
        "type": "tile",
        "zoom_level": 14,
        "properties_map": {
            "kiken_type_ja": "区域種別",
            "gensyo_type_ja": "現象種別"
        }
    },
    "XKT003": {
        "name": "立地適正化計画",
        "endpoint": "XKT003",
        "type": "tile",
        "zoom_level": 14,
        "properties_map": {
            "area_type_ja": "区域種別"
        }
    },
    "XKT024": {
        "name": "地区計画",
        "endpoint": "XKT024",
        "type": "tile",
        "zoom_level": 14,
        "properties_map": {
            "name": "地区計画名"
        }
    },
    "XKT030": {
        "name": "都市計画道路",
        "endpoint": "XKT030",
        "type": "tile",
        "zoom_level": 14,
        "properties_map": {
            "road_name": "道路名",
            "width": "幅員"
        }
    },
    # 価格情報系（クエリパラメータ方式）
    "XIT001": {
        "name": "価格情報",
        "endpoint": "XIT001",
        "type": "query",
        "required_params": ["year", "area"]
    }
}


class ReinfLibClient:
    """不動産情報ライブラリAPIクライアント"""

    BASE_URL = settings.REINFOLIB_BASE_URL

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: APIキー（省略時は環境変数REINFOLIB_API_KEYを使用）
        """
        self.api_key = api_key or os.getenv("REINFOLIB_API_KEY")
        if not self.api_key:
            raise ValueError("REINFOLIB_API_KEY環境変数が設定されていません")

        self.session = requests.Session()
        self.session.headers.update({
            "Ocp-Apim-Subscription-Key": self.api_key
        })

    def _request(self, endpoint: str, params: dict) -> dict:
        """APIリクエスト共通処理"""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {endpoint} - {e}")
            raise

    def get_tile_data(
        self,
        api_code: str,
        lat: float,
        lng: float,
        response_format: str = "geojson"
    ) -> dict:
        """
        タイル系APIからデータ取得（単一タイル）

        Args:
            api_code: API識別子（XKT002等）
            lat: 緯度
            lng: 経度
            response_format: レスポンス形式（geojson/pbf）

        Returns:
            GeoJSONデータ
        """
        api_def = API_DEFINITIONS.get(api_code)
        if not api_def or api_def["type"] != "tile":
            raise ValueError(f"Invalid tile API code: {api_code}")

        zoom = api_def["zoom_level"]
        x, y = lat_lng_to_tile(lat, lng, zoom)

        params = {
            "response_format": response_format,
            "z": zoom,
            "x": x,
            "y": y
        }

        return self._request(api_def["endpoint"], params)

    def get_tile_data_wide(
        self,
        api_code: str,
        lat: float,
        lng: float,
        radius: int = 1
    ) -> dict:
        """
        タイル系APIから広域データ取得（周辺タイルも含む）

        Args:
            api_code: API識別子（XKT002等）
            lat: 緯度
            lng: 経度
            radius: 取得範囲（1=3x3, 2=5x5）

        Returns:
            マージされたGeoJSONデータ
        """
        api_def = API_DEFINITIONS.get(api_code)
        if not api_def or api_def["type"] != "tile":
            raise ValueError(f"Invalid tile API code: {api_code}")

        zoom = api_def["zoom_level"]
        center_x, center_y = lat_lng_to_tile(lat, lng, zoom)

        all_features = []
        seen_geometries = set()

        # 周辺タイルを取得（3x3 or 5x5）
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy

                try:
                    params = {
                        "response_format": "geojson",
                        "z": zoom,
                        "x": x,
                        "y": y
                    }
                    data = self._request(api_def["endpoint"], params)
                    features = data.get("features", [])

                    for feature in features:
                        # 重複排除（geometryのハッシュで判定）
                        geom_str = str(feature.get("geometry", {}).get("coordinates", []))
                        if geom_str not in seen_geometries:
                            seen_geometries.add(geom_str)
                            all_features.append(feature)

                except Exception as e:
                    logger.warning(f"Failed to get tile ({x}, {y}): {e}")
                    continue

        return {
            "type": "FeatureCollection",
            "features": all_features
        }

    def get_regulation_at_point(
        self,
        api_code: str,
        lat: float,
        lng: float
    ) -> Optional[dict]:
        """
        指定座標の規制情報を取得

        Args:
            api_code: API識別子
            lat: 緯度
            lng: 経度

        Returns:
            該当する規制情報（properties）、該当なしの場合None
        """
        try:
            geojson = self.get_tile_data(api_code, lat, lng)
            features = geojson.get("features", [])

            if not features:
                return None

            # preferred_kubun_ids: 対象kubun_idでフィルタ+優先順ソート
            api_def = API_DEFINITIONS.get(api_code, {})
            preferred = api_def.get("preferred_kubun_ids")
            if preferred:
                preferred_set = set(preferred)
                features = [
                    f for f in features
                    if f.get("properties", {}).get("kubun_id") in preferred_set
                ]
                priority = {k: i for i, k in enumerate(preferred)}
                features.sort(
                    key=lambda f: priority.get(
                        f.get("properties", {}).get("kubun_id"), 999
                    )
                )

            # 座標を含むfeatureを検索
            feature = find_containing_feature(lat, lng, features)
            if feature:
                return feature.get("properties", {})

            return None

        except Exception as e:
            logger.error(f"Failed to get regulation at point: {api_code} ({lat}, {lng}) - {e}")
            return None

    def get_all_regulations(self, lat: float, lng: float) -> dict:
        """
        指定座標の全規制情報を一括取得

        Args:
            lat: 緯度
            lng: 経度

        Returns:
            {
                "use_area": {"用途地域": "商業地域", "建ぺい率": "80%", ...},
                "fire_prevention": {"防火地域区分": "準防火地域"},
                "flood": {"浸水深": "0.5〜3m", ...},
                "landslide": None,  # 該当なし
                ...
            }
        """
        results = {}

        # 都市計画区域・区域区分（XKT001）
        props = self.get_regulation_at_point("XKT001", lat, lng)
        results["city_planning"] = self._map_properties("XKT001", props) if props else None

        # 用途地域
        props = self.get_regulation_at_point("XKT002", lat, lng)
        results["use_area"] = self._map_properties("XKT002", props) if props else None

        # 防火地域
        props = self.get_regulation_at_point("XKT014", lat, lng)
        results["fire_prevention"] = self._map_properties("XKT014", props) if props else None

        # 洪水浸水想定
        props = self.get_regulation_at_point("XKT026", lat, lng)
        results["flood"] = self._map_properties("XKT026", props) if props else None

        # 土砂災害警戒
        props = self.get_regulation_at_point("XKT029", lat, lng)
        results["landslide"] = self._map_properties("XKT029", props) if props else None

        # 津波浸水想定
        props = self.get_regulation_at_point("XKT028", lat, lng)
        results["tsunami"] = self._map_properties("XKT028", props) if props else None

        # 高潮浸水想定
        props = self.get_regulation_at_point("XKT027", lat, lng)
        results["storm_surge"] = self._map_properties("XKT027", props) if props else None

        # 立地適正化計画
        props = self.get_regulation_at_point("XKT003", lat, lng)
        results["location_optimization"] = self._map_properties("XKT003", props) if props else None

        # 地区計画
        props = self.get_regulation_at_point("XKT024", lat, lng)
        results["district_plan"] = self._map_properties("XKT024", props) if props else None

        # 都市計画道路
        props = self.get_regulation_at_point("XKT030", lat, lng)
        results["planned_road"] = self._map_properties("XKT030", props) if props else None

        return results

    def _map_properties(self, api_code: str, props: dict) -> dict:
        """
        APIレスポンスのproperties を日本語キーにマッピング

        Args:
            api_code: API識別子
            props: 元のproperties

        Returns:
            日本語キーにマッピングされたdict
        """
        api_def = API_DEFINITIONS.get(api_code, {})
        prop_map = api_def.get("properties_map", {})

        result = {}
        for eng_key, ja_key in prop_map.items():
            if eng_key in props and props[eng_key]:
                result[ja_key] = props[eng_key]

        return result

    def get_price_info(
        self,
        year: int,
        area: str,
        city: Optional[str] = None,
        from_period: Optional[str] = None,
        to_period: Optional[str] = None
    ) -> dict:
        """
        価格情報を取得

        Args:
            year: 年（例: 2023）
            area: 都道府県コード（例: "01" = 北海道）
            city: 市区町村コード（オプション）
            from_period: 開始期（例: "20231" = 2023年第1四半期）
            to_period: 終了期

        Returns:
            価格情報データ
        """
        params = {
            "year": year,
            "area": area
        }
        if city:
            params["city"] = city
        if from_period:
            params["from"] = from_period
        if to_period:
            params["to"] = to_period

        return self._request("XIT001", params)

    @staticmethod
    def get_available_apis() -> dict:
        """利用可能なAPI一覧を取得"""
        return {
            code: {
                "name": defn["name"],
                "type": defn["type"]
            }
            for code, defn in API_DEFINITIONS.items()
        }
