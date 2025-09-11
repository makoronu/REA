"""
REA不動産業務専用ユーティリティ
価格計算、利回り計算、築年数計算等の不動産特化機能
"""

import re
from typing import Optional
from datetime import datetime


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
    price_text = price_text.replace(',', '')
    
    # 価格パターン
    patterns = [
        (r'(\d+)億(\d+)万円', lambda m: float(m.group(1)) * 100000000 + float(m.group(2)) * 10000),
        (r'(\d+)億円', lambda m: float(m.group(1)) * 100000000),
        (r'(\d+)万円', lambda m: float(m.group(1)) * 10000),
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
    match = re.search(r'(\d+(?:\.\d+)?)', area_text)
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
    match = re.search(r'(\d{4})年', text)
    if match:
        return int(match.group(1))
    
    # 和暦変換
    wareki_patterns = [
        ('令和', r'令和(\d+)年', 2018),
        ('平成', r'平成(\d+)年', 1988),
        ('昭和', r'昭和(\d+)年', 1925),
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
    if '/kodate/' in url:
        return '戸建て'
    elif '/mansion/' in url:
        return 'マンション'
    elif '/tochi/' in url:
        return '土地'
    
    # タイトルから判定
    if title:
        title_lower = title.lower()
        if 'マンション' in title_lower:
            return 'マンション'
        elif '土地' in title_lower:
            return '土地'
        else:
            return '戸建て'
    
    return '戸建て'  # デフォルト


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


def format_price_display(price: Optional[float]) -> str:
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


def calculate_yield(price: Optional[float], monthly_rent: Optional[float]) -> Optional[float]:
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
    if any(word in property_type for word in ['戸建', '一戸建', '一軒家']):
        return '戸建て'
    elif any(word in property_type for word in ['マンション', 'アパート']):
        return 'マンション'
    elif any(word in property_type for word in ['土地', '更地']):
        return '土地'
    elif any(word in property_type for word in ['店舗', '事務所', '倉庫']):
        return '事業用'
    else:
        return property_type  # そのまま返す