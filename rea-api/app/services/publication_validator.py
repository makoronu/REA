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
- 最小選択数: column_labels.min_selections
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
# 旧カラム(management_fee, repair_reserve_fund)は廃止済み
# 現在zero_is_validなカラムはDBから読み込み
_DEFAULT_ZERO_VALID_COLUMNS: set[str] = set()
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


def get_min_selections(db: Session, column_name: str) -> Optional[int]:
    """
    カラムの最小選択数を取得

    Args:
        db: DBセッション
        column_name: カラム名

    Returns:
        最小選択数（設定なしの場合はNone）
    """
    try:
        query = text("""
            SELECT min_selections
            FROM column_labels
            WHERE column_name = :column_name
              AND min_selections IS NOT NULL
            LIMIT 1
        """)
        result = db.execute(query, {"column_name": column_name}).fetchone()
        if result and result.min_selections is not None:
            return result.min_selections
    except Exception as e:
        logger.warning(f"Failed to get min_selections for {column_name}: {e}")
    return None


def get_column_labels_batch(db: Session, column_names: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    複数カラムのvalid_none_text・min_selectionsを一括取得（N+1解消用）

    Args:
        db: DBセッション
        column_names: カラム名リスト

    Returns:
        {column_name: {"valid_none_text": [...], "min_selections": int|None}}
    """
    if not column_names:
        return {}

    try:
        query = text("""
            SELECT column_name, valid_none_text, min_selections
            FROM column_labels
            WHERE column_name = ANY(:column_names)
        """)
        result = db.execute(query, {"column_names": column_names})
        labels = {}
        for row in result:
            labels[row.column_name] = {
                "valid_none_text": row.valid_none_text if row.valid_none_text else None,
                "min_selections": row.min_selections,
            }
        return labels
    except Exception as e:
        logger.warning(f"Failed to batch load column_labels: {e}")
        return {}


def get_validation_groups(db: Session, property_type: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    validation_groupでグループ化されたフィールドを取得
    同じグループのフィールドは「いずれか1つtrue」を要求

    Args:
        db: DBセッション
        property_type: 物件種別

    Returns:
        {
            "property_purpose": [
                {"column_name": "is_residential", "japanese_label": "居住用"},
                {"column_name": "is_commercial", "japanese_label": "事業用"},
                {"column_name": "is_investment", "japanese_label": "投資用"},
            ],
            ...
        }
    """
    try:
        query = text("""
            SELECT column_name, japanese_label, validation_group, group_name
            FROM column_labels
            WHERE validation_group IS NOT NULL
              AND (visible_for IS NULL OR :property_type = ANY(visible_for))
            ORDER BY validation_group, display_order
        """)
        result = db.execute(query, {"property_type": property_type})

        groups: Dict[str, List[Dict[str, Any]]] = {}
        for row in result:
            group_key = row.validation_group
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append({
                "column_name": row.column_name,
                "japanese_label": row.japanese_label or row.column_name,
                "group_name": row.group_name or "その他",
            })
        return groups
    except Exception as e:
        logger.warning(f"Failed to get validation_groups: {e}")
        return {}


def get_conditional_exclusions(db: Session) -> Dict[str, Dict[str, Any]]:
    """
    条件付き除外ルールを取得

    Returns:
        {
            "building_coverage_ratio": {"depends_on": "use_district", "exclude_when_option_value": ["無指定"]},
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
        "building_coverage_ratio": {"depends_on": "use_district", "exclude_when_option_value": ["無指定"]},
        "floor_area_ratio": {"depends_on": "use_district", "exclude_when_option_value": ["無指定"]},
        "room_floor": {"depends_on": "property_type", "exclude_when": ["detached"]},
        "total_units": {"depends_on": "property_type", "exclude_when": ["detached"]},
        "setback": {"depends_on": "road_info", "exclude_when_flag": "no_road_access"},
    }


def get_option_value_by_id(db: Session, option_id: int, category_code: str) -> Optional[str]:
    """
    マスタオプションIDから表示名を取得

    Args:
        db: DBセッション
        option_id: マスタオプションのoption_code（整数）
        category_code: カテゴリコード（column_labels.master_category_codeから取得）

    Returns:
        option_value（表示名）またはNone
    """
    try:
        query = text("""
            SELECT mo.option_value
            FROM master_options mo
            JOIN master_categories mc ON mo.category_id = mc.id
            WHERE mc.category_code = :category_code
              AND mo.option_code = :option_code
              AND mo.is_active = TRUE
        """)
        result = db.execute(query, {
            "category_code": category_code,
            "option_code": str(option_id)
        }).fetchone()
        if result:
            return result.option_value
    except Exception as e:
        logger.warning(f"Failed to get option_value for {category_code}/{option_id}: {e}")
    return None


def get_master_category_code(db: Session, column_name: str) -> Optional[str]:
    """
    カラム名からマスタカテゴリコードを取得

    Returns:
        master_category_code またはNone
    """
    try:
        query = text("""
            SELECT master_category_code
            FROM column_labels
            WHERE column_name = :column_name
              AND master_category_code IS NOT NULL
            LIMIT 1
        """)
        result = db.execute(query, {"column_name": column_name}).fetchone()
        if result:
            return result.master_category_code
    except Exception as e:
        logger.warning(f"Failed to get master_category_code for {column_name}: {e}")
    return None


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
    min_selections: Optional[int] = None,
) -> bool:
    """
    値が有効（入力済み）かどうかを判定

    Args:
        value: 判定対象の値
        column_name: カラム名
        zero_valid_columns: 0が有効なカラム集合
        special_flag_keys: 特殊フラグキーマッピング
        valid_none_values: 「なし」として有効なテキスト値
        min_selections: 最小選択数（配列型フィールド用、Noneの場合は1以上）

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
        # min_selectionsが設定されている場合はその値以上かチェック
        required_count = min_selections if min_selections is not None else 1
        return len(value) >= required_count

    return True


def should_exclude_field(
    db: Session,
    column_name: str,
    property_data: Dict[str, Any],
    conditional_exclusions: Dict[str, Dict[str, Any]],
    special_flag_keys: Dict[str, str],
) -> bool:
    """
    条件付き除外の判定

    Args:
        db: DBセッション
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

    # マスタオプション表示名での判定（exclude_when_option_value）
    if "exclude_when_option_value" in rule:
        exclude_values = rule.get("exclude_when_option_value", [])
        category_code = get_master_category_code(db, depends_on)
        if not category_code:
            return False

        # JSONB配列対応: ["rea_4"] のような形式
        if isinstance(depends_value, list):
            for code in depends_value:
                option_value = get_option_value_by_id(db, code, category_code)
                if option_value and option_value in exclude_values:
                    return True
            return False

        # 後方互換: 整数または文字列
        if isinstance(depends_value, (int, str)):
            option_value = get_option_value_by_id(db, depends_value, category_code)
            if option_value and option_value in exclude_values:
                return True
        return False

    # 値ベースの判定（exclude_when）- 後方互換性のため残す
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

    非表示カラム（visible_forに含まれない）はバリデーション対象外

    Returns:
        [{"table_name": "properties", "column_name": "property_name", "japanese_label": "物件名", "group_name": "基本情報"}, ...]
    """
    query = text("""
        SELECT table_name, column_name, japanese_label, group_name
        FROM column_labels
        WHERE required_for_publication IS NOT NULL
          AND :property_type = ANY(required_for_publication)
          AND (visible_for IS NULL OR :property_type = ANY(visible_for))
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

    # valid_none_text・min_selectionsを一括取得（N+1解消）
    required_column_names = [f["column_name"] for f in required_fields]
    column_labels_map = get_column_labels_batch(db, required_column_names)

    # 未入力フィールドをチェック
    missing_fields = []
    for field in required_fields:
        column_name = field["column_name"]

        # 条件付き除外チェック
        if should_exclude_field(db, column_name, property_data, conditional_exclusions, special_flag_keys):
            continue

        value = property_data.get(column_name)

        # バッチ取得結果から読み出し（フォールバック付き）
        col_info = column_labels_map.get(column_name, {})
        valid_none_values = col_info.get("valid_none_text") or _DEFAULT_VALID_NONE_VALUES
        min_selections = col_info.get("min_selections")

        # 有効値判定
        if not is_valid_value(value, column_name, zero_valid_columns, special_flag_keys, valid_none_values, min_selections):
            missing_fields.append({
                "label": field["japanese_label"],
                "group": field["group_name"],
            })

    if missing_fields:
        return False, missing_fields

    # validation_groupチェック（同じグループで「いずれか1つtrue」を要求）
    validation_groups = get_validation_groups(db, property_type)
    for group_name, group_fields in validation_groups.items():
        # グループ内のフィールドで1つでもtrueがあればOK
        has_true_value = False
        for field in group_fields:
            value = property_data.get(field["column_name"])
            if value is True:
                has_true_value = True
                break

        if not has_true_value:
            # グループ内で1つもtrueがない場合はエラー
            labels = [f["japanese_label"] for f in group_fields]
            missing_fields.append({
                "label": f"「{'」「'.join(labels)}」のいずれか",
                "group": group_fields[0]["group_name"] if group_fields else "その他",
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
