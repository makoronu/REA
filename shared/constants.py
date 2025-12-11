"""
REA共通定数・関数

複数箇所で使われる定数や計算ロジックを一元管理
"""

# =============================================================================
# 距離・時間計算
# =============================================================================

WALK_SPEED_METERS_PER_MIN = 80  # 不動産公正取引協議会基準: 80m/分


def calc_walk_minutes(distance_meters: float) -> int:
    """
    距離（メートル）から徒歩分数を計算

    Args:
        distance_meters: 距離（メートル）

    Returns:
        徒歩分数（最低1分）
    """
    return max(1, round(distance_meters / WALK_SPEED_METERS_PER_MIN))


# =============================================================================
# 学校種別コード（国土数値情報 P29）
# =============================================================================

SCHOOL_TYPE_CODES = {
    'elementary': '16001',      # 小学校
    'junior_high': '16002',     # 中学校
    'high_school': '16003',     # 高等学校
    'university': '16004',      # 大学
    'junior_college': '16005',  # 短期大学
    'technical_college': '16006',  # 高等専門学校
    'special_needs': '16007',   # 特別支援学校
    'kindergarten': '16008',    # 幼稚園
    'certified_childcare': '16009',  # 認定こども園
    'vocational': '16010',      # 専修学校（専門学校）
}

# 学区として使うもの
SCHOOL_DISTRICT_TYPES = {
    'elementary': SCHOOL_TYPE_CODES['elementary'],
    'junior_high': SCHOOL_TYPE_CODES['junior_high'],
}


# =============================================================================
# 検索デフォルト値
# =============================================================================

DEFAULT_SEARCH_RADIUS = {
    'station': 5000,      # 駅検索: 5km
    'bus_stop': 2000,     # バス停検索: 2km
    'facility': 1000,     # 周辺施設検索: 1km
    'school': 3000,       # 学校検索: 3km
}

DEFAULT_MAX_ITEMS = {
    'station': 10,        # 最寄駅: 最大10件
    'bus_stop': 5,        # バス停: 最大5件
    'facility': 50,       # 周辺施設: 最大50件
    'school': 5,          # 学校候補: 最大5件
}
