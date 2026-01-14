"""
管理者用API
フィールド表示設定など

リファクタリング: 2025-12-15
- 共通関数抽出
- カスタム例外使用

修正: 2026-01-14
- updated_at, updated_by を設定するよう修正（プロトコル遵守）
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.exceptions import DatabaseError
from shared.auth.middleware import get_current_user

router = APIRouter()


class FieldVisibilityUpdate(BaseModel):
    """フィールド設定更新用（表示/必須両対応）"""
    table_name: str
    column_name: str
    visible_for: Optional[List[str]] = None
    required_for_publication: Optional[List[str]] = None


class PropertyTypeInfo(BaseModel):
    """物件種別情報"""
    id: str
    label: str
    group_name: str


# ========================================
# 共通関数
# ========================================

def _execute_field_settings_update(
    db: Session,
    update: FieldVisibilityUpdate,
    field_type: str = "visibility",
    updated_by: Optional[str] = None,
) -> None:
    """単一のフィールド設定を更新（共通処理）

    field_type:
    - "visibility": visible_for を更新（表示設定）
    - "required": required_for_publication を更新（必須設定）

    値の意味（両方共通）:
    - None: 未設定（全種別適用 or 任意）
    - []: 空配列（どの種別にも適用しない）
    - ['mansion', ...]: 指定種別のみ適用
    """
    if field_type == "required":
        column_name_sql = "required_for_publication"
        value = update.required_for_publication
    else:
        column_name_sql = "visible_for"
        value = update.visible_for

    if value is None:
        query = text(f"""
            UPDATE column_labels
            SET {column_name_sql} = NULL,
                updated_at = NOW(),
                updated_by = :updated_by
            WHERE table_name = :table_name AND column_name = :column_name
        """)
        db.execute(query, {
            "table_name": update.table_name,
            "column_name": update.column_name,
            "updated_by": updated_by,
        })
    else:
        query = text(f"""
            UPDATE column_labels
            SET {column_name_sql} = :value,
                updated_at = NOW(),
                updated_by = :updated_by
            WHERE table_name = :table_name AND column_name = :column_name
        """)
        db.execute(query, {
            "table_name": update.table_name,
            "column_name": update.column_name,
            "value": value,
            "updated_by": updated_by,
        })


# ========================================
# エンドポイント
# ========================================

@router.get("/property-types", response_model=List[PropertyTypeInfo])
def get_property_types(db: Session = Depends(dependencies.get_db)) -> List[PropertyTypeInfo]:
    """物件種別一覧を取得（グループ付き）"""
    try:
        query = text("""
            SELECT id, label, group_name
            FROM property_types
            ORDER BY group_name, label
        """)
        result = db.execute(query)
        return [
            PropertyTypeInfo(id=row.id, label=row.label, group_name=row.group_name)
            for row in result
        ]
    except Exception as e:
        raise DatabaseError(str(e))


@router.get("/field-visibility", response_model=List[Dict[str, Any]])
def get_field_visibility(
    table_name: Optional[str] = None,
    db: Session = Depends(dependencies.get_db)
) -> List[Dict[str, Any]]:
    """フィールド設定一覧を取得（表示設定・必須設定両方含む）"""
    try:
        if table_name:
            query = text("""
                SELECT table_name, column_name, japanese_label, visible_for,
                       required_for_publication, group_name,
                       COALESCE(group_order, 999) as group_order,
                       COALESCE(display_order, 999) as display_order
                FROM column_labels
                WHERE table_name = :table_name
                ORDER BY group_order, display_order, column_name
            """)
            result = db.execute(query, {"table_name": table_name})
        else:
            query = text("""
                SELECT table_name, column_name, japanese_label, visible_for,
                       required_for_publication, group_name,
                       COALESCE(group_order, 999) as group_order,
                       COALESCE(display_order, 999) as display_order
                FROM column_labels
                WHERE table_name IN ('properties', 'building_info', 'land_info', 'amenities')
                ORDER BY table_name, group_order, display_order, column_name
            """)
            result = db.execute(query)

        return [
            {
                "table_name": row.table_name,
                "column_name": row.column_name,
                "japanese_label": row.japanese_label,
                "visible_for": row.visible_for,
                "required_for_publication": row.required_for_publication,
                "group_name": row.group_name,
                "group_order": row.group_order,
                "display_order": row.display_order,
            }
            for row in result
        ]
    except Exception as e:
        raise DatabaseError(str(e))


@router.put("/field-visibility")
def update_field_visibility(
    update: FieldVisibilityUpdate,
    request: Request,
    field_type: str = "visibility",
    db: Session = Depends(dependencies.get_db),
) -> Dict[str, Any]:
    """フィールド設定を更新

    Args:
        field_type: "visibility"（表示設定）または "required"（必須設定）
    """
    try:
        user = get_current_user(request)
        updated_by = user.get("email") if user else None

        _execute_field_settings_update(db, update, field_type, updated_by)
        db.commit()

        result_value = (
            update.required_for_publication if field_type == "required"
            else update.visible_for
        )
        return {
            "success": True,
            "message": f"Updated {update.table_name}.{update.column_name}",
            "field_type": field_type,
            "value": result_value,
        }
    except Exception as e:
        db.rollback()
        raise DatabaseError(str(e))


@router.put("/field-visibility/bulk")
def update_field_visibility_bulk(
    updates: List[FieldVisibilityUpdate],
    request: Request,
    field_type: str = "visibility",
    db: Session = Depends(dependencies.get_db),
) -> Dict[str, Any]:
    """フィールド設定を一括更新

    Args:
        field_type: "visibility"（表示設定）または "required"（必須設定）
    """
    try:
        user = get_current_user(request)
        updated_by = user.get("email") if user else None

        for update in updates:
            _execute_field_settings_update(db, update, field_type, updated_by)

        db.commit()

        return {
            "success": True,
            "message": f"Updated {len(updates)} fields",
            "field_type": field_type,
            "updated_count": len(updates),
        }
    except Exception as e:
        db.rollback()
        raise DatabaseError(str(e))
