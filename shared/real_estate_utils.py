"""
REA不動産業務専用ユーティリティ
価格計算、利回り計算、築年数計算等の不動産特化機能
"""

import re
from datetime import datetime
from typing import Optional


def parse_sale_price(price_text: str) -> Optional[float]:
    """
    売買価格をパース

    Args:
        price_text: 価格文字列（例: "1200万円", "1億2000万円"）

    Returns:
        float: パースされた価格（円単位）
        None: パースできない場合

    Examples:
        >>> parse_sale_price("1200万円")
        12000000.0
        >>> parse_sale_price("1億2000万円")
        120000000.0
    """
    # カンマを削除
    price_text = price_text.replace(",", "")

    # 価格パターン
    patterns = [
        (
            r"(\d+)億(\d+)万円",
            lambda m: float(m.group(1)) * 100000000 + float(m.group(2)) * 10000,
        ),
        (r"(\d+)億円", lambda m: float(m.group(1)) * 100000000),
        (r"(\d+)万円", lambda m: float(m.group(1)) * 10000),
    ]

    for pattern, converter in patterns:
        match = re.search(pattern, price_text)
        if match:
            return converter(match)

    return None


def parse_area(area_text: str) -> Optional[float]:
    """
    面積をパース

    Args:
        area_text: 面積文字列（例: "50.5㎡", "100平米"）

    Returns:
        float: パースされた面積（㎡単位）
        None: パースできない場合

    Examples:
        >>> parse_area("50.5㎡")
        50.5
        >>> parse_area("100平米")
        100.0
    """
    match = re.search(r"(\d+(?:\.\d+)?)", area_text)
    if match:
        return float(match.group(1))
    return None


def parse_construction_year(text: str) -> Optional[int]:
    """
    築年月から年を抽出

    Args:
        text: 築年月文字列（例: "令和3年", "2021年", "平成30年"）

    Returns:
        int: 西暦年
        None: パースできない場合

    Examples:
        >>> parse_construction_year("令和3年")
        2021
        >>> parse_construction_year("平成30年")
        2018
    """
    # 西暦
    match = re.search(r"(\d{4})年", text)
    if match:
        return int(match.group(1))

    # 和暦変換
    wareki_patterns = [
        ("令和", r"令和(\d+)年", 2018),
        ("平成", r"平成(\d+)年", 1988),
        ("昭和", r"昭和(\d+)年", 1925),
    ]

    for era_name, pattern, base_year in wareki_patterns:
        if era_name in text:
            match = re.search(pattern, text)
            if match:
                return base_year + int(match.group(1))

    return None


def determine_property_type(url: str, title: str = "") -> str:
    """
    物件タイプを判定

    Args:
        url: 物件URL
        title: 物件タイトル（オプション）

    Returns:
        str: 物件タイプ（戸建て/マンション/土地）

    Examples:
        >>> determine_property_type("https://homes.co.jp/kodate/b-123/")
        "戸建て"
        >>> determine_property_type("https://homes.co.jp/mansion/b-456/")
        "マンション"
    """
    # URLから判定
    if "/kodate/" in url:
        return "戸建て"
    elif "/mansion/" in url:
        return "マンション"
    elif "/tochi/" in url:
        return "土地"

    # タイトルから判定
    if title:
        title_lower = title.lower()
        if "マンション" in title_lower:
            return "マンション"
        elif "土地" in title_lower:
            return "土地"
        else:
            return "戸建て"

    return "戸建て"  # デフォルト


def calculate_property_age(construction_year: Optional[int]) -> Optional[int]:
    """
    築年数を計算

    Args:
        construction_year: 建築年（西暦）

    Returns:
        int: 築年数
        None: 計算できない場合

    Examples:
        >>> calculate_property_age(2020)
        5  # 2025年の場合
    """
    if construction_year is None:
        return None

    current_year = datetime.now().year
    age = current_year - construction_year
    return max(0, age)  # 負の値にはならない


def format_price_display(price) -> str:
    """
    価格を表示用にフォーマット

    Args:
        price: 価格（円単位）

    Returns:
        str: フォーマットされた価格文字列

    Examples:
        >>> format_price_display(12000000)
        "1,200万円"
        >>> format_price_display(120000000)
        "1億2,000万円"
    """
    price = to_float(price)
    if price is None:
        return "価格未定"

    if price >= 100000000:  # 1億円以上
        oku = int(price // 100000000)
        man = int((price % 100000000) // 10000)
        if man > 0:
            return f"{oku}億{man:,}万円"
        else:
            return f"{oku}億円"
    elif price >= 10000:  # 1万円以上
        man = int(price // 10000)
        return f"{man:,}万円"
    else:
        return f"{int(price):,}円"


def calculate_yield(price, monthly_rent) -> Optional[float]:
    """
    表面利回りを計算

    Args:
        price: 物件価格（円）
        monthly_rent: 月額賃料（円）

    Returns:
        float: 表面利回り（%）
        None: 計算できない場合

    Examples:
        >>> calculate_yield(12000000, 80000)
        8.0
    """
    price = to_float(price)
    monthly_rent = to_float(monthly_rent)
    if price is None or monthly_rent is None or price <= 0:
        return None

    annual_rent = monthly_rent * 12
    yield_rate = (annual_rent / price) * 100
    return round(yield_rate, 2)


def normalize_property_type(property_type: str) -> str:
    """
    物件種別を正規化

    Args:
        property_type: 物件種別文字列

    Returns:
        str: 正規化された物件種別

    Examples:
        >>> normalize_property_type("一戸建て")
        "戸建て"
        >>> normalize_property_type("分譲マンション")
        "マンション"
    """
    # 正規化ルール
    if any(word in property_type for word in ["戸建", "一戸建", "一軒家"]):
        return "戸建て"
    elif any(word in property_type for word in ["マンション", "アパート"]):
        return "マンション"
    elif any(word in property_type for word in ["土地", "更地"]):
        return "土地"
    elif any(word in property_type for word in ["店舗", "事務所", "倉庫"]):
        return "事業用"
    else:
        return property_type  # そのまま返す


# ==================================================
# チラシ・マイソク用フォーマット関数
# ==================================================

from decimal import Decimal

SQM_TO_TSUBO = 0.3025  # 1㎡ = 0.3025坪


def to_float(value) -> Optional[float]:
    """値をfloatに変換（Decimal対応）"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def format_area_with_tsubo(sqm) -> str:
    """
    面積を㎡（坪）形式で表示

    Args:
        sqm: 面積（㎡）

    Returns:
        str: フォーマットされた面積文字列

    Examples:
        >>> format_area_with_tsubo(100.5)
        '100.50㎡（30.40坪）'
    """
    sqm = to_float(sqm)
    if sqm is None:
        return "面積未定"
    tsubo = sqm * SQM_TO_TSUBO
    return f"{sqm:.2f}㎡（{tsubo:.2f}坪）"


def format_area_tsubo_only(sqm) -> str:
    """
    面積を坪のみで表示

    Args:
        sqm: 面積（㎡）

    Returns:
        str: 坪数文字列

    Examples:
        >>> format_area_tsubo_only(100.0)
        '30.25坪'
    """
    sqm = to_float(sqm)
    if sqm is None:
        return "未定"
    tsubo = sqm * SQM_TO_TSUBO
    return f"{tsubo:.2f}坪"


def format_price_man(price: Optional[float]) -> str:
    """
    価格を万円表示（1億以上は億円併記）
    format_price_displayのエイリアス（設計ドキュメント準拠）

    Args:
        price: 価格（円単位）

    Returns:
        str: フォーマットされた価格文字列
    """
    return format_price_display(price)


def format_price_per_tsubo(price, sqm) -> str:
    """
    坪単価を表示

    Args:
        price: 価格（円単位）
        sqm: 面積（㎡）

    Returns:
        str: 坪単価文字列

    Examples:
        >>> format_price_per_tsubo(30000000, 100.0)
        '約99万円/坪'
    """
    price = to_float(price)
    sqm = to_float(sqm)
    if price is None or sqm is None or sqm <= 0:
        return "坪単価未定"
    tsubo = sqm * SQM_TO_TSUBO
    price_per_tsubo = price / tsubo
    man = int(price_per_tsubo // 10000)
    return f"約{man:,}万円/坪"


def format_building_age(construction_date) -> str:
    """
    築年数を表示

    Args:
        construction_date: 建築年月日（date, datetime, or str）

    Returns:
        str: 築年数文字列

    Examples:
        >>> from datetime import date
        >>> format_building_age(date(2010, 3, 1))
        '築15年（平成22年築）'  # 2025年の場合
    """
    if construction_date is None:
        return "築年数不詳"

    # 文字列の場合はパース
    if isinstance(construction_date, str):
        year = parse_construction_year(construction_date)
        if year is None:
            return "築年数不詳"
    else:
        # date or datetime
        year = construction_date.year

    current_year = datetime.now().year
    age = current_year - year
    wareki = format_wareki_year(year)
    return f"築{age}年（{wareki}築）"


def format_wareki_year(year: int) -> str:
    """
    西暦を和暦に変換

    Args:
        year: 西暦年

    Returns:
        str: 和暦文字列

    Examples:
        >>> format_wareki_year(2020)
        '令和2年'
        >>> format_wareki_year(2000)
        '平成12年'
        >>> format_wareki_year(1980)
        '昭和55年'
    """
    if year >= 2019:
        return f"令和{year - 2018}年"
    elif year >= 1989:
        return f"平成{year - 1988}年"
    elif year >= 1926:
        return f"昭和{year - 1925}年"
    elif year >= 1912:
        return f"大正{year - 1911}年"
    else:
        return f"明治{year - 1867}年"


def format_percentage(value) -> str:
    """
    パーセンテージ表示

    Args:
        value: 数値（既にパーセント値の場合）

    Returns:
        str: パーセンテージ文字列

    Examples:
        >>> format_percentage(60.5)
        '60.5%'
    """
    value = to_float(value)
    if value is None:
        return "未定"
    return f"{value}%"


def format_floor_display(floor: Optional[int]) -> str:
    """
    階数表示

    Args:
        floor: 階数

    Returns:
        str: 階数文字列

    Examples:
        >>> format_floor_display(3)
        '3階'
        >>> format_floor_display(-1)
        '地下1階'
    """
    if floor is None:
        return "階数未定"
    if floor < 0:
        return f"地下{abs(floor)}階"
    return f"{floor}階"
