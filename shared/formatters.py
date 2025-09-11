"""
REAフォーマット処理統一システム
住所、電話番号、日付等の統一フォーマット処理
"""

import re
from typing import Optional


def normalize_address(address: str) -> str:
    """
    住所を正規化

    Args:
        address: 住所文字列

    Returns:
        str: 正規化された住所

    Examples:
        >>> normalize_address("東京都　新宿区西新宿１－２－３")
        "東京都新宿区西新宿1-2-3"
    """
    if not address:
        return ""

    # 全角数字を半角に変換
    address = address.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

    # 全角英字を半角に変換
    address = address.translate(
        str.maketrans("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    )

    # 全角ハイフンを半角に変換
    address = address.replace("－", "-").replace("ー", "-")

    # 余分な空白を削除
    address = re.sub(r"\s+", "", address)

    # 改行を削除
    address = address.replace("\n", "").replace("\r", "")

    # 不要なテキストを削除
    remove_patterns = [
        r"地図を見る.*",
        r"無料.*",
        r"詳細な所在地を教えてほしい.*",
        r"GoogleMapで見る.*",
        r"周辺環境を見る.*",
    ]

    for pattern in remove_patterns:
        address = re.sub(pattern, "", address, flags=re.IGNORECASE)

    return address.strip()


def clean_phone_number(phone_text: str) -> Optional[str]:
    """
    電話番号をクリーニング

    Args:
        phone_text: 電話番号文字列

    Returns:
        str: 正規化された電話番号（03-1234-5678形式）
        None: 有効な電話番号でない場合

    Examples:
        >>> clean_phone_number("０３（１２３４）５６７８")
        "03-1234-5678"
        >>> clean_phone_number("0312345678")
        "03-1234-5678"
    """
    if not phone_text:
        return None

    # 全角数字を半角に変換
    phone_text = phone_text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

    # 数字とハイフンのみを抽出
    cleaned = re.sub(r"[^\d-]", "", phone_text)

    # ハイフンを一旦削除して数字のみにする
    digits_only = re.sub(r"[^\d]", "", cleaned)

    # 10桁または11桁の場合のみ処理
    if len(digits_only) == 10:
        # 03-1234-5678 形式
        return f"{digits_only[:2]}-{digits_only[2:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11:
        # 090-1234-5678 形式
        return f"{digits_only[:3]}-{digits_only[3:7]}-{digits_only[7:]}"
    elif len(digits_only) == 12 and digits_only.startswith("81"):
        # 国際番号を削除して再処理
        return clean_phone_number(digits_only[2:])

    # 既にハイフン形式の場合はそのまま返す
    if re.match(r"^\d{2,4}-\d{2,4}-\d{3,4}$", cleaned):
        return cleaned

    return None


def extract_listing_id(url: str, prefix: str = "homes") -> Optional[str]:
    """
    URLから物件ID抽出

    Args:
        url: 物件URL
        prefix: IDのプレフィックス

    Returns:
        str: 抽出されたID
        None: IDが見つからない場合

    Examples:
        >>> extract_listing_id("https://homes.co.jp/kodate/b-12345/", "homes")
        "homes_12345"
    """
    if not url:
        return None

    # ホームズの物件IDパターン
    match = re.search(r"/b-(\d+)/", url)
    if match:
        return f"{prefix}_{match.group(1)}"

    # 他のパターンも対応可能
    # URLの最後の数字を取得
    match = re.search(r"/(\d+)/?$", url)
    if match:
        return f"{prefix}_{match.group(1)}"

    return None


def format_date_japanese(date_str: str) -> str:
    """
    日付を日本語形式にフォーマット

    Args:
        date_str: 日付文字列

    Returns:
        str: 日本語形式の日付

    Examples:
        >>> format_date_japanese("2025-01-15")
        "2025年1月15日"
    """
    if not date_str:
        return ""

    # ISO形式の場合
    match = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}年{int(month)}月{int(day)}日"

    return date_str


def format_area_display(area: Optional[float], unit: str = "㎡") -> str:
    """
    面積を表示用にフォーマット

    Args:
        area: 面積
        unit: 単位

    Returns:
        str: フォーマットされた面積文字列

    Examples:
        >>> format_area_display(50.5)
        "50.5㎡"
        >>> format_area_display(100.0, "坪")
        "100.0坪"
    """
    if area is None:
        return "面積未定"

    # 小数点以下が0の場合は整数表示
    if area == int(area):
        return f"{int(area)}{unit}"
    else:
        return f"{area:.1f}{unit}"


def clean_text_content(text: str) -> str:
    """
    テキストコンテンツをクリーニング

    Args:
        text: クリーニング対象のテキスト

    Returns:
        str: クリーニング済みテキスト
    """
    if not text:
        return ""

    # 余分な空白・改行を削除
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    # HTMLエンティティをデコード
    html_entities = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
        "&nbsp;": " ",
    }

    for entity, char in html_entities.items():
        text = text.replace(entity, char)

    return text


def normalize_company_name(company_name: str) -> str:
    """
    会社名を正規化

    Args:
        company_name: 会社名

    Returns:
        str: 正規化された会社名

    Examples:
        >>> normalize_company_name("（株）サンプル不動産")
        "株式会社サンプル不動産"
    """
    if not company_name:
        return ""

    # 全角括弧を半角に
    company_name = company_name.replace("（", "(").replace("）", ")")

    # 略称を正式名称に変換
    replacements = [
        (r"\(株\)", "株式会社"),
        (r"株\)", "株式会社"),
        (r"\(有\)", "有限会社"),
        (r"有\)", "有限会社"),
        (r"\(合\)", "合同会社"),
        (r"合\)", "合同会社"),
    ]

    for pattern, replacement in replacements:
        company_name = re.sub(pattern, replacement, company_name)

    return clean_text_content(company_name)


def extract_numeric_value(text: str) -> Optional[float]:
    """
    テキストから数値を抽出

    Args:
        text: テキスト

    Returns:
        float: 抽出された数値
        None: 数値が見つからない場合

    Examples:
        >>> extract_numeric_value("面積50.5㎡")
        50.5
        >>> extract_numeric_value("価格1,200万円")
        1200.0
    """
    if not text:
        return None

    # カンマを削除
    text = text.replace(",", "")

    # 数値を抽出
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if match:
        return float(match.group(1))

    return None


def format_floor_plan(floor_plan: str) -> str:
    """
    間取りを正規化

    Args:
        floor_plan: 間取り文字列

    Returns:
        str: 正規化された間取り

    Examples:
        >>> format_floor_plan("３ＬＤＫ")
        "3LDK"
    """
    if not floor_plan:
        return ""

    # 全角を半角に変換
    floor_plan = floor_plan.translate(
        str.maketrans(
            "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ",
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        )
    )

    # 余分な文字を削除
    floor_plan = re.sub(r"[^\dLDKRS+]", "", floor_plan.upper())

    return floor_plan
