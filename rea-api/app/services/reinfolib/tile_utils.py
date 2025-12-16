"""
タイル座標変換ユーティリティ

緯度経度 ⇔ XYZタイル座標の変換
"""
import math
from typing import Tuple


def lat_lng_to_tile(lat: float, lng: float, zoom: int) -> Tuple[int, int]:
    """
    緯度経度からタイル座標(x, y)を計算

    Args:
        lat: 緯度（-90〜90）
        lng: 経度（-180〜180）
        zoom: ズームレベル（0〜20）

    Returns:
        (x, y) タイル座標
    """
    n = 2 ** zoom
    x = int((lng + 180) / 360 * n)
    lat_rad = math.radians(lat)
    y = int((1 - math.asinh(math.tan(lat_rad)) / math.pi) / 2 * n)
    return x, y


def tile_to_lat_lng(x: int, y: int, zoom: int) -> Tuple[float, float]:
    """
    タイル座標から緯度経度を計算（タイル左上の座標）

    Args:
        x: タイルX座標
        y: タイルY座標
        zoom: ズームレベル

    Returns:
        (lat, lng) 緯度経度
    """
    n = 2 ** zoom
    lng = x / n * 360 - 180
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat = math.degrees(lat_rad)
    return lat, lng


def get_tile_bounds(x: int, y: int, zoom: int) -> dict:
    """
    タイルの境界ボックスを取得

    Returns:
        {"north": 北端緯度, "south": 南端緯度, "west": 西端経度, "east": 東端経度}
    """
    north, west = tile_to_lat_lng(x, y, zoom)
    south, east = tile_to_lat_lng(x + 1, y + 1, zoom)
    return {
        "north": north,
        "south": south,
        "west": west,
        "east": east
    }


def point_in_polygon(lat: float, lng: float, polygon_coords: list) -> bool:
    """
    点がポリゴン内にあるかを判定（Ray casting algorithm）

    Args:
        lat: 緯度
        lng: 経度
        polygon_coords: [[lng, lat], [lng, lat], ...] 形式のポリゴン座標

    Returns:
        True if point is inside polygon
    """
    n = len(polygon_coords)
    inside = False

    p1_lng, p1_lat = polygon_coords[0]
    for i in range(1, n + 1):
        p2_lng, p2_lat = polygon_coords[i % n]
        if lat > min(p1_lat, p2_lat):
            if lat <= max(p1_lat, p2_lat):
                if lng <= max(p1_lng, p2_lng):
                    if p1_lat != p2_lat:
                        lng_intersect = (lat - p1_lat) * (p2_lng - p1_lng) / (p2_lat - p1_lat) + p1_lng
                    if p1_lng == p2_lng or lng <= lng_intersect:
                        inside = not inside
        p1_lng, p1_lat = p2_lng, p2_lat

    return inside


def find_containing_feature(lat: float, lng: float, features: list) -> dict | None:
    """
    指定座標を含むGeoJSON featureを検索

    Args:
        lat: 緯度
        lng: 経度
        features: GeoJSON features配列

    Returns:
        含まれるfeature、なければNone
    """
    for feature in features:
        geometry = feature.get("geometry", {})
        geom_type = geometry.get("type", "")
        coords = geometry.get("coordinates", [])

        if geom_type == "Polygon":
            # 外周のみチェック（穴は無視）
            if coords and point_in_polygon(lat, lng, coords[0]):
                return feature
        elif geom_type == "MultiPolygon":
            for polygon in coords:
                if polygon and point_in_polygon(lat, lng, polygon[0]):
                    return feature

    return None
