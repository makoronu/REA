"""
公開時バリデーション

公開ステータスが「公開」または「会員公開」に変更される際に、
required_for_publication で設定された必須項目が入力されているかをチェック。
"""
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text


# 公開時にバリデーションが必要なステータス
PUBLICATION_STATUSES_REQUIRING_VALIDATION = ["公開", "会員公開"]


def get_required_fields(db: Session, property_type: str) -> List[Dict[str, Any]]:
    """
    指定された物件種別で必須となるフィールド一覧を取得

    Returns:
        [{"table_name": "properties", "column_name": "property_name", "japanese_label": "物件名"}, ...]
    """
    query = text("""
        SELECT table_name, column_name, japanese_label
        FROM column_labels
        WHERE required_for_publication IS NOT NULL
          AND :property_type = ANY(required_for_publication)
        ORDER BY table_name, column_name
    """)
    result = db.execute(query, {"property_type": property_type})
    return [
        {
            "table_name": row.table_name,
            "column_name": row.column_name,
            "japanese_label": row.japanese_label or row.column_name,
        }
        for row in result
    ]


def validate_for_publication(
    db: Session,
    property_data: Dict[str, Any],
    new_publication_status: Optional[str],
    current_publication_status: Optional[str] = None,
) -> Tuple[bool, List[str]]:
    """
    公開時バリデーションを実行

    Args:
        db: DBセッション
        property_data: 物件データ（現在 + 更新データのマージ済み）
        new_publication_status: 更新後の公開ステータス
        current_publication_status: 現在の公開ステータス（既に公開中なら再チェック不要の判断用）

    Returns:
        (is_valid, missing_fields): バリデーション結果と未入力フィールド名のリスト
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
        return False, ["物件種別が未設定です"]

    # 必須フィールド一覧を取得
    required_fields = get_required_fields(db, property_type)

    if not required_fields:
        # 必須設定がない場合はOK
        return True, []

    # 未入力フィールドをチェック
    missing_fields = []
    for field in required_fields:
        column_name = field["column_name"]
        value = property_data.get(column_name)

        # 未入力判定: None, 空文字, 空白のみ
        if value is None or (isinstance(value, str) and not value.strip()):
            missing_fields.append(field["japanese_label"])

    if missing_fields:
        return False, missing_fields

    return True, []


def format_validation_error(missing_fields: List[str], publication_status: str) -> str:
    """
    バリデーションエラーメッセージをフォーマット
    """
    fields_str = "、".join(missing_fields)
    return f"「{publication_status}」にするには以下の項目が必要です: {fields_str}"
