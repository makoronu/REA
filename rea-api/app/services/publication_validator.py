"""
公開時バリデーション

公開ステータスが「公開」または「会員公開」に変更される際に、
required_for_publication で設定された必須項目が入力されているかをチェック。

設定はすべてDBから読み込み（メタデータ駆動）:
- バリデーション必要ステータス: master_options.requires_validation
- 「なし」有効値: column_labels.valid_none_text
- 0有効カラム: column_labels.zero_is_valid
- 条件付き除外: column_labels.conditional_exclusion
- 特殊フラグ: column_labels.special_flag_key
"""
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# フォールバック用デフォルト値（DB読み込み失敗時に使用）
# =============================================================================

_DEFAULT_PUBLICATION_STATUSES = ["公開", "会員公開"]
_DEFAULT_VALID_NONE_VALUES = ["なし", "該当なし", "なし（学区外）"]
_DEFAULT_ZERO_VALID_COLUMNS = {"management_fee", "repair_reserve_fund"}
_DEFAULT_SPECIAL_FLAG_KEYS = {
    "road_info": "no_road_access",
    "transportation": "no_station",
    "bus_stops": "no_bus",
    "nearby_facilities": "no_facilities",
}


# =============================================================================
# DB設定読み込み関数
# =============================================================================

def get_validation_required_statuses(db: Session) -> List[str]:
    """
    バリデーションが必要な公開ステータス一覧を取得

    Returns:
        ["公開", "会員公開"] 等
    """
    try:
        query = text("""
            SELECT mo.option_value
            FROM master_options mo
            JOIN master_categories mc ON mo.category_id = mc.id
            WHERE mc.category_code = 'publication_status'
              AND mo.requires_validation = TRUE
              AND mo.is_active = TRUE
        """)
        result = db.execute(query)
        statuses = [row.option_value for row in result]
        if statuses:
            return statuses
    except Exception as e:
        logger.warning(f"Failed to load validation_required_statuses from DB: {e}")

    return _DEFAULT_PUBLICATION_STATUSES


def get_zero_valid_columns(db: Session) -> Set[str]:
    """
    0が有効値となるカラム一覧を取得

    Returns:
        {"management_fee", "repair_reserve_fund"} 等
    """
    try:
        query = text("""
            SELECT column_name
            FROM column_labels
            WHERE zero_is_valid = TRUE
        """)
        result = db.execute(query)
        columns = {row.column_name for row in result}
        if columns:
            return columns
    except Exception as e:
        logger.warning(f"Failed to load zero_valid_columns from DB: {e}")

    return _DEFAULT_ZERO_VALID_COLUMNS


def get_special_flag_keys(db: Session) -> Dict[str, str]:
    """
    特殊フラグのキー名マッピングを取得

    Returns:
        {"road_info": "no_road_access", "transportation": "no_station", ...}
    """
    try:
        query = text("""
            SELECT column_name, special_flag_key
            FROM column_labels
            WHERE special_flag_key IS NOT NULL
        """)
        result = db.execute(query)
        mapping = {row.column_name: row.special_flag_key for row in result}
        if mapping:
            return mapping
    except Exception as e:
        logger.warning(f"Failed to load special_flag_keys from DB: {e}")

    return _DEFAULT_SPECIAL_FLAG_KEYS


def get_conditional_exclusions(db: Session) -> Dict[str, Dict[str, Any]]:
    """
    条件付き除外ルールを取得

    Returns:
        {
            "building_coverage_ratio": {"depends_on": "use_district", "exclude_when": ["none", "指定なし"]},
            "setback": {"depends_on": "road_info", "exclude_when_flag": "no_road_access"},
            ...
        }
    """
    try:
        query = text("""
            SELECT column_name, conditional_exclusion
            FROM column_labels
            WHERE conditional_exclusion IS NOT NULL
        """)
        result = db.execute(query)
        exclusions = {}
        for row in result:
            if row.conditional_exclusion:
                exclusions[row.column_name] = row.conditional_exclusion
        if exclusions:
            return exclusions
    except Exception as e:
        logger.warning(f"Failed to load conditional_exclusions from DB: {e}")

    # フォールバック
    return {
        "building_coverage_ratio": {"depends_on": "use_district", "exclude_when": ["none", "指定なし"]},
        "floor_area_ratio": {"depends_on": "use_district", "exclude_when": ["none", "指定なし"]},
        "room_floor": {"depends_on": "property_type", "exclude_when": ["detached"]},
        "total_units": {"depends_on": "property_type", "exclude_when": ["detached"]},
        "setback": {"depends_on": "road_info", "exclude_when_flag": "no_road_access"},
    }


def get_valid_none_text(db: Session, column_name: str) -> List[str]:
    """
    カラム別の「なし」有効値を取得

    Returns:
        ["なし", "該当なし"] 等
    """
    try:
        query = text("""
            SELECT valid_none_text
            FROM column_labels
            WHERE column_name = :column_name
              AND valid_none_text IS NOT NULL
        """)
        result = db.execute(query, {"column_name": column_name}).fetchone()
        if result and result.valid_none_text:
            return result.valid_none_text
    except Exception as e:
        logger.warning(f"Failed to load valid_none_text for {column_name}: {e}")

    return _DEFAULT_VALID_NONE_VALUES


# =============================================================================
# 特殊フラグ判定
# =============================================================================

def has_special_flag(value: Any, flag_key: str) -> bool:
    """
    特殊フラグの有無を判定

    Args:
        value: 判定対象の値（dict想定）
        flag_key: フラグキー名（"no_road_access"等）

    Returns:
        True: フラグが設定されている
    """
    if isinstance(value, dict) and value.get(flag_key) is True:
        return True
    return False


# =============================================================================
# 有効値判定
# =============================================================================

def is_valid_value(
    value: Any,
    column_name: str,
    zero_valid_columns: Set[str],
    special_flag_keys: Dict[str, str],
    valid_none_values: List[str],
) -> bool:
    """
    値が有効（入力済み）かどうかを判定

    Args:
        value: 判定対象の値
        column_name: カラム名
        zero_valid_columns: 0が有効なカラム集合
        special_flag_keys: 特殊フラグキーマッピング
        valid_none_values: 「なし」として有効なテキスト値

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
        if value.strip() in valid_none_values:
            return True
        return True

    # 数値の場合
    if isinstance(value, (int, float)):
        # 0が有効なカラムはTrueを返す
        if column_name in zero_valid_columns:
            return True
        return True

    # 辞書の場合（特殊フラグ対応）
    if isinstance(value, dict):
        # 特殊フラグカラムの場合
        if column_name in special_flag_keys:
            flag_key = special_flag_keys[column_name]
            if has_special_flag(value, flag_key):
                return True  # 「なし」フラグは有効値
        # 通常のdict（空でなければ有効）
        return bool(value)

    # 配列の場合
    if isinstance(value, list):
        return len(value) > 0

    return True


def should_exclude_field(
    column_name: str,
    property_data: Dict[str, Any],
    conditional_exclusions: Dict[str, Dict[str, Any]],
    special_flag_keys: Dict[str, str],
) -> bool:
    """
    条件付き除外の判定

    Args:
        column_name: 判定対象カラム名
        property_data: 物件データ
        conditional_exclusions: 条件付き除外ルール
        special_flag_keys: 特殊フラグキーマッピング

    Returns:
        True: このフィールドはチェック対象外
        False: チェック対象
    """
    rule = conditional_exclusions.get(column_name)
    if not rule:
        return False

    depends_on = rule.get("depends_on")
    depends_value = property_data.get(depends_on)

    # フラグベースの判定（exclude_when_flag）
    if "exclude_when_flag" in rule:
        flag_key = rule["exclude_when_flag"]
        if has_special_flag(depends_value, flag_key):
            return True
        return False

    # 値ベースの判定（exclude_when）
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
    # DBから設定を読み込み
    validation_statuses = get_validation_required_statuses(db)

    # 公開/会員公開への変更でない場合はスキップ
    if new_publication_status not in validation_statuses:
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

    # DBから各種設定を読み込み
    zero_valid_columns = get_zero_valid_columns(db)
    special_flag_keys = get_special_flag_keys(db)
    conditional_exclusions = get_conditional_exclusions(db)

    # 未入力フィールドをチェック
    missing_fields = []
    for field in required_fields:
        column_name = field["column_name"]

        # 条件付き除外チェック
        if should_exclude_field(column_name, property_data, conditional_exclusions, special_flag_keys):
            continue

        value = property_data.get(column_name)

        # カラム別の「なし」有効値を取得
        valid_none_values = get_valid_none_text(db, column_name)

        # 有効値判定
        if not is_valid_value(value, column_name, zero_valid_columns, special_flag_keys, valid_none_values):
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
