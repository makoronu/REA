"""
公開時バリデーション

公開ステータスが「公開」または「会員公開」に変更される際に、
required_for_publication で設定された必須項目が入力されているかをチェック。

条件付き除外ルール:
- 用途地域「指定なし」→ 建ぺい率・容積率不要
- 物件種別「detached」→ 所在階・総戸数不要
- 接道情報「接道なし」→ セットバック不要

特殊フラグ対応:
- road_info: { "no_road_access": true }
- transportation: { "no_station": true }
- bus_stops: { "no_bus": true }
- nearby_facilities: { "no_facilities": true }
"""
from typing import Any, Callable, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text


# 公開時にバリデーションが必要なステータス
PUBLICATION_STATUSES_REQUIRING_VALIDATION = ["公開", "会員公開"]

# 「なし」として有効なテキスト値
VALID_NONE_VALUES = ["なし", "該当なし", "なし（学区外）"]

# 0が有効値となるカラム
ZERO_VALID_COLUMNS = ["management_fee", "repair_reserve_fund"]


# =============================================================================
# 特殊フラグ判定関数
# =============================================================================

def is_no_road_access(value: Any) -> bool:
    """接道なしフラグの判定"""
    if isinstance(value, dict) and value.get("no_road_access") is True:
        return True
    return False


def is_no_station(value: Any) -> bool:
    """最寄駅なしフラグの判定"""
    if isinstance(value, dict) and value.get("no_station") is True:
        return True
    return False


def is_no_bus(value: Any) -> bool:
    """バス路線なしフラグの判定"""
    if isinstance(value, dict) and value.get("no_bus") is True:
        return True
    return False


def is_no_facilities(value: Any) -> bool:
    """近隣施設なしフラグの判定"""
    if isinstance(value, dict) and value.get("no_facilities") is True:
        return True
    return False


# 特殊フラグカラムとその判定関数
SPECIAL_FLAG_COLUMNS: Dict[str, Callable[[Any], bool]] = {
    "road_info": is_no_road_access,
    "transportation": is_no_station,
    "bus_stops": is_no_bus,
    "nearby_facilities": is_no_facilities,
}


# =============================================================================
# 条件付き除外ルール
# =============================================================================

CONDITIONAL_EXCLUSIONS: Dict[str, Dict[str, Any]] = {
    # 用途地域が「指定なし」の場合、建ぺい率・容積率は不要
    "building_coverage_ratio": {
        "depends_on": "use_district",
        "exclude_when": ["none", "指定なし"],
    },
    "floor_area_ratio": {
        "depends_on": "use_district",
        "exclude_when": ["none", "指定なし"],
    },
    # 戸建の場合、所在階・総戸数は不要
    "room_floor": {
        "depends_on": "property_type",
        "exclude_when": ["detached"],
    },
    "total_units": {
        "depends_on": "property_type",
        "exclude_when": ["detached"],
    },
    # 接道なしの場合、セットバックは不要
    "setback": {
        "depends_on": "road_info",
        "exclude_when_func": is_no_road_access,
    },
}


# =============================================================================
# 有効値判定
# =============================================================================

def is_valid_value(value: Any, column_name: str) -> bool:
    """
    値が有効（入力済み）かどうかを判定

    Args:
        value: 判定対象の値
        column_name: カラム名

    Returns:
        True: 有効な値（入力済み）
        False: 無効な値（未入力・空）
    """
    if value is None:
        return False

    # 文字列の場合
    if isinstance(value, str):
        if not value.strip():
            return False
        # 「なし」系テキストは有効
        if value.strip() in VALID_NONE_VALUES:
            return True
        return True

    # 数値の場合
    if isinstance(value, (int, float)):
        # 特定カラムは0を有効値とする
        if column_name in ZERO_VALID_COLUMNS:
            return True
        return True

    # 辞書の場合（特殊フラグ対応）
    if isinstance(value, dict):
        # 特殊フラグカラムの場合
        if column_name in SPECIAL_FLAG_COLUMNS:
            check_func = SPECIAL_FLAG_COLUMNS[column_name]
            if check_func(value):
                return True  # 「なし」フラグは有効値
        # 通常のdict（空でなければ有効）
        return bool(value)

    # 配列の場合
    if isinstance(value, list):
        return len(value) > 0

    return True


def should_exclude_field(column_name: str, property_data: Dict[str, Any]) -> bool:
    """
    条件付き除外の判定

    Args:
        column_name: 判定対象カラム名
        property_data: 物件データ

    Returns:
        True: このフィールドはチェック対象外
        False: チェック対象
    """
    rule = CONDITIONAL_EXCLUSIONS.get(column_name)
    if not rule:
        return False

    depends_on = rule.get("depends_on")
    depends_value = property_data.get(depends_on)

    # 関数ベースの判定
    if "exclude_when_func" in rule:
        func = rule["exclude_when_func"]
        if callable(func) and func(depends_value):
            return True
        return False

    # 値ベースの判定
    exclude_when = rule.get("exclude_when", [])
    if depends_value in exclude_when:
        return True

    # マスタオプションの値チェック（code or valueどちらでもマッチ）
    if isinstance(depends_value, (int, str)):
        str_value = str(depends_value)
        for exclude_val in exclude_when:
            if str_value == str(exclude_val):
                return True

    return False


def get_required_fields(db: Session, property_type: str) -> List[Dict[str, Any]]:
    """
    指定された物件種別で必須となるフィールド一覧を取得

    Returns:
        [{"table_name": "properties", "column_name": "property_name", "japanese_label": "物件名", "group_name": "基本情報"}, ...]
    """
    query = text("""
        SELECT table_name, column_name, japanese_label, group_name
        FROM column_labels
        WHERE required_for_publication IS NOT NULL
          AND :property_type = ANY(required_for_publication)
        ORDER BY COALESCE(group_order, 999), COALESCE(display_order, 999)
    """)
    result = db.execute(query, {"property_type": property_type})
    return [
        {
            "table_name": row.table_name,
            "column_name": row.column_name,
            "japanese_label": row.japanese_label or row.column_name,
            "group_name": row.group_name or "その他",
        }
        for row in result
    ]


def validate_for_publication(
    db: Session,
    property_data: Dict[str, Any],
    new_publication_status: Optional[str],
    current_publication_status: Optional[str] = None,
) -> Tuple[bool, List[Dict[str, str]]]:
    """
    公開時バリデーションを実行

    Args:
        db: DBセッション
        property_data: 物件データ（現在 + 更新データのマージ済み）
        new_publication_status: 更新後の公開ステータス
        current_publication_status: 現在の公開ステータス（既に公開中なら再チェック不要の判断用）

    Returns:
        (is_valid, missing_fields): バリデーション結果と未入力フィールド情報のリスト
        missing_fields: [{"label": "物件名", "group": "基本情報"}, ...]
    """
    # 公開/会員公開への変更でない場合はスキップ
    if new_publication_status not in PUBLICATION_STATUSES_REQUIRING_VALIDATION:
        return True, []

    # 既に同じ公開ステータスの場合はスキップ（ステータス変更なし）
    if new_publication_status == current_publication_status:
        return True, []

    # 物件種別を取得
    property_type = property_data.get("property_type")
    if not property_type:
        return False, [{"label": "物件種別が未設定です", "group": "基本情報"}]

    # 必須フィールド一覧を取得
    required_fields = get_required_fields(db, property_type)

    if not required_fields:
        # 必須設定がない場合はOK
        return True, []

    # 未入力フィールドをチェック
    missing_fields = []
    for field in required_fields:
        column_name = field["column_name"]

        # 条件付き除外チェック
        if should_exclude_field(column_name, property_data):
            continue

        value = property_data.get(column_name)

        # 有効値判定（改善版）
        if not is_valid_value(value, column_name):
            missing_fields.append({
                "label": field["japanese_label"],
                "group": field["group_name"],
            })

    if missing_fields:
        return False, missing_fields

    return True, []


def format_validation_error(missing_fields: List[Dict[str, str]], publication_status: str) -> str:
    """
    バリデーションエラーメッセージをフォーマット（シンプル版）
    """
    labels = [f["label"] for f in missing_fields]
    fields_str = "、".join(labels)
    return f"「{publication_status}」にするには以下の項目が必要です: {fields_str}"


def format_validation_error_grouped(missing_fields: List[Dict[str, str]], publication_status: str) -> Dict[str, Any]:
    """
    バリデーションエラーをグループ別に整形（詳細版）

    Returns:
        {
            "message": "「公開」にするには以下の項目が必要です",
            "groups": {
                "基本情報": ["物件名", "物件種別"],
                "所在地": ["郵便番号", "住所"],
                ...
            }
        }
    """
    groups: Dict[str, List[str]] = {}
    for field in missing_fields:
        group = field["group"]
        if group not in groups:
            groups[group] = []
        groups[group].append(field["label"])

    return {
        "message": f"「{publication_status}」にするには以下の項目が必要です",
        "groups": groups,
    }
