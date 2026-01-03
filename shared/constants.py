"""
REA共通定数・関数

メタデータ駆動: 設定値はsystem_configテーブルから取得
フォールバック: DB接続失敗時はデフォルト値を使用
キャッシュ: 起動時に1回読み込み、以降はキャッシュを使用
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# =============================================================================
# 設定キャッシュ（起動時に1回読み込み）
# =============================================================================

_config_cache: Dict[str, Any] = {}
_config_loaded: bool = False


def _load_config_from_db() -> Dict[str, Any]:
    """DBから設定を読み込み"""
    try:
        from shared.database import READatabase

        result = READatabase.execute_query_dict(
            "SELECT config_key, config_value FROM system_config"
        )
        return {row['config_key']: row['config_value'] for row in result}
    except Exception as e:
        logger.warning(f"Failed to load config from DB, using defaults: {e}")
        return {}


def get_config(key: str, default: Any = None) -> Any:
    """設定値を取得（キャッシュ付き）"""
    global _config_cache, _config_loaded

    if not _config_loaded:
        _config_cache = _load_config_from_db()
        _config_loaded = True

    return _config_cache.get(key, default)


def reload_config() -> None:
    """設定を再読み込み（テスト用）"""
    global _config_cache, _config_loaded
    _config_cache = _load_config_from_db()
    _config_loaded = True


# =============================================================================
# デフォルト値（DB接続失敗時のフォールバック）
# =============================================================================

_DEFAULT_SCHOOL_TYPE_CODES: Dict[str, str] = {
    'elementary': '16001',
    'junior_high': '16002',
    'high_school': '16003',
    'university': '16004',
    'junior_college': '16005',
    'technical_college': '16006',
    'special_needs': '16007',
    'kindergarten': '16008',
    'certified_childcare': '16009',
    'vocational': '16010',
}

_DEFAULT_SEARCH_RADIUS: Dict[str, int] = {
    'station': 5000,
    'bus_stop': 2000,
    'facility': 1000,
    'school': 3000,
}

_DEFAULT_MAX_ITEMS: Dict[str, int] = {
    'station': 10,
    'bus_stop': 5,
    'facility': 50,
    'school': 5,
    'nearest_stations_form': 15,
    'nearest_bus_stops_form': 15,
    'facility_per_category': 5,
}


# =============================================================================
# 公開API（メタデータ駆動 + フォールバック）
# =============================================================================

def get_school_type_codes() -> Dict[str, str]:
    """学校種別コードを取得"""
    return get_config('school_type_codes', _DEFAULT_SCHOOL_TYPE_CODES)


def get_school_district_types() -> Dict[str, str]:
    """学区用学校種別を取得"""
    codes = get_school_type_codes()
    return get_config('school_district_types', {
        'elementary': codes.get('elementary', '16001'),
        'junior_high': codes.get('junior_high', '16002'),
    })


def get_search_radius() -> Dict[str, int]:
    """検索半径設定を取得"""
    return get_config('search_radius', _DEFAULT_SEARCH_RADIUS)


def get_max_items() -> Dict[str, int]:
    """最大取得件数設定を取得"""
    return get_config('max_items', _DEFAULT_MAX_ITEMS)


def get_display_order_fallback() -> int:
    """表示順序フォールバック値を取得"""
    return get_config('display_order_fallback', 999)


def get_walk_speed() -> int:
    """徒歩速度（メートル/分）を取得"""
    return get_config('walk_speed_meters_per_min', 80)


def get_property_type_group_order() -> Dict[str, int]:
    """
    物件種別グループのソート順序を取得

    DBのproperty_typesテーブルから動的に取得
    """
    try:
        from shared.database import READatabase

        result = READatabase.execute_query_dict(
            "SELECT DISTINCT group_name, MIN(sort_order) as sort_order "
            "FROM property_types "
            "WHERE deleted_at IS NULL "
            "GROUP BY group_name "
            "ORDER BY sort_order"
        )
        return {row['group_name']: row['sort_order'] for row in result if row['group_name']}
    except Exception as e:
        logger.warning(f"Failed to get property type group order: {e}")
        return {'居住用': 1, '事業用': 2, '投資用': 3}


# =============================================================================
# 距離・時間計算
# =============================================================================

# 不動産公正取引協議会基準: 80m/分（法令で定められた値）
WALK_SPEED_METERS_PER_MIN: int = 80


def calc_walk_minutes(distance_meters: float) -> int:
    """
    距離（メートル）から徒歩分数を計算

    Args:
        distance_meters: 距離（メートル）

    Returns:
        徒歩分数（最低1分）
    """
    speed = get_walk_speed()
    return max(1, round(distance_meters / speed))


# =============================================================================
# 後方互換性のための遅延評価クラス
# =============================================================================

class _LazyDict(dict):
    """遅延評価するdict"""

    def __init__(self, loader):
        self._loader = loader
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            data = self._loader()
            super().update(data)
            self._loaded = True

    def __getitem__(self, key):
        self._ensure_loaded()
        return super().__getitem__(key)

    def __contains__(self, key):
        self._ensure_loaded()
        return super().__contains__(key)

    def get(self, key, default=None):
        self._ensure_loaded()
        return super().get(key, default)

    def items(self):
        self._ensure_loaded()
        return super().items()

    def keys(self):
        self._ensure_loaded()
        return super().keys()

    def values(self):
        self._ensure_loaded()
        return super().values()

    def __iter__(self):
        self._ensure_loaded()
        return super().__iter__()

    def __repr__(self):
        self._ensure_loaded()
        return super().__repr__()


# =============================================================================
# 後方互換性のためのモジュールレベル変数
# これらは既存コードで from shared.constants import XXX として使用される
# =============================================================================

SCHOOL_TYPE_CODES: Dict[str, str] = _LazyDict(get_school_type_codes)
SCHOOL_DISTRICT_TYPES: Dict[str, str] = _LazyDict(get_school_district_types)
DEFAULT_SEARCH_RADIUS: Dict[str, int] = _LazyDict(get_search_radius)
DEFAULT_MAX_ITEMS: Dict[str, int] = _LazyDict(get_max_items)
DEFAULT_DISPLAY_ORDER_FALLBACK: int = 999  # 固定値（起動時に評価が必要な場合はget_display_order_fallback()を使用）
PROPERTY_TYPE_GROUP_ORDER: Dict[str, int] = _LazyDict(get_property_type_group_order)
