"""
管理者用API
フィールド表示設定など

リファクタリング: 2025-12-15
- 共通関数抽出
- カスタム例外使用
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.exceptions import DatabaseError

router = APIRouter()


class FieldVisibilityUpdate(BaseModel):
    """フィールド表示設定更新用"""
    table_name: str
    column_name: str
    visible_for: Optional[List[str]] = None


class PropertyTypeInfo(BaseModel):
    """物件種別情報"""
    id: str
    label: str
    group_name: str


# ========================================
# 共通関数
# ========================================

def _execute_visibility_update(db: Session, update: FieldVisibilityUpdate) -> None:
    """単一のフィールド表示設定を更新（共通処理）

    visible_for の意味:
    - None: 未設定（全種別表示）
    - []: 空配列（どの種別にも表示しない）
    - ['mansion', ...]: 指定種別のみ表示
    """
    if update.visible_for is None:
        # None → NULL（未設定状態、全種別表示）
        query = text("""
            UPDATE column_labels
            SET visible_for = NULL
            WHERE table_name = :table_name AND column_name = :column_name
        """)
        db.execute(query, {
            "table_name": update.table_name,
            "column_name": update.column_name,
        })
    else:
        # 空配列または値あり → そのまま保存
        query = text("""
            UPDATE column_labels
            SET visible_for = :visible_for
            WHERE table_name = :table_name AND column_name = :column_name
        """)
        db.execute(query, {
            "table_name": update.table_name,
            "column_name": update.column_name,
            "visible_for": update.visible_for,
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
    """フィールド表示設定一覧を取得"""
    try:
        if table_name:
            query = text("""
                SELECT table_name, column_name, japanese_label, visible_for, group_name,
                       COALESCE(group_order, 999) as group_order,
                       COALESCE(display_order, 999) as display_order
                FROM column_labels
                WHERE table_name = :table_name
                ORDER BY group_order, display_order, column_name
            """)
            result = db.execute(query, {"table_name": table_name})
        else:
            query = text("""
                SELECT table_name, column_name, japanese_label, visible_for, group_name,
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
    db: Session = Depends(dependencies.get_db)
) -> Dict[str, Any]:
    """フィールド表示設定を更新"""
    try:
        _execute_visibility_update(db, update)
        db.commit()

        return {
            "success": True,
            "message": f"Updated {update.table_name}.{update.column_name}",
            "visible_for": update.visible_for,
        }
    except Exception as e:
        db.rollback()
        raise DatabaseError(str(e))


@router.put("/field-visibility/bulk")
def update_field_visibility_bulk(
    updates: List[FieldVisibilityUpdate],
    db: Session = Depends(dependencies.get_db)
) -> Dict[str, Any]:
    """フィールド表示設定を一括更新"""
    try:
        for update in updates:
            _execute_visibility_update(db, update)

        db.commit()

        return {
            "success": True,
            "message": f"Updated {len(updates)} fields",
            "updated_count": len(updates),
        }
    except Exception as e:
        db.rollback()
        raise DatabaseError(str(e))
