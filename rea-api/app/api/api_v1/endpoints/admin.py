"""
管理者用API
フィールド表示設定など
"""
from typing import Any, Dict, List, Optional

from app.api import dependencies
from app.core.database import engine
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

router = APIRouter()


class FieldVisibilityUpdate(BaseModel):
    """フィールド表示設定更新用"""
    table_name: str
    column_name: str
    visible_for: Optional[List[str]] = None  # Noneで全種別表示


class PropertyTypeInfo(BaseModel):
    """物件種別情報"""
    id: str
    label: str
    group_name: str


@router.get("/property-types", response_model=List[PropertyTypeInfo])
def get_property_types(db: Session = Depends(dependencies.get_db)) -> List[PropertyTypeInfo]:
    """
    物件種別一覧を取得（グループ付き）
    """
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/field-visibility", response_model=List[Dict[str, Any]])
def get_field_visibility(
    table_name: Optional[str] = None,
    db: Session = Depends(dependencies.get_db)
) -> List[Dict[str, Any]]:
    """
    フィールド表示設定一覧を取得
    """
    try:
        if table_name:
            query = text("""
                SELECT table_name, column_name, japanese_label, visible_for, group_name
                FROM column_labels
                WHERE table_name = :table_name
                ORDER BY display_order, column_name
            """)
            result = db.execute(query, {"table_name": table_name})
        else:
            query = text("""
                SELECT table_name, column_name, japanese_label, visible_for, group_name
                FROM column_labels
                WHERE table_name IN ('properties', 'building_info', 'land_info', 'amenities')
                ORDER BY table_name, display_order, column_name
            """)
            result = db.execute(query)

        return [
            {
                "table_name": row.table_name,
                "column_name": row.column_name,
                "japanese_label": row.japanese_label,
                "visible_for": row.visible_for,
                "group_name": row.group_name,
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/field-visibility")
def update_field_visibility(
    update: FieldVisibilityUpdate,
    db: Session = Depends(dependencies.get_db)
) -> Dict[str, Any]:
    """
    フィールド表示設定を更新
    """
    try:
        # visible_forがNoneまたは空配列の場合はNULLに設定
        if update.visible_for is None or len(update.visible_for) == 0:
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

        db.commit()

        return {
            "success": True,
            "message": f"Updated {update.table_name}.{update.column_name}",
            "visible_for": update.visible_for,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/field-visibility/bulk")
def update_field_visibility_bulk(
    updates: List[FieldVisibilityUpdate],
    db: Session = Depends(dependencies.get_db)
) -> Dict[str, Any]:
    """
    フィールド表示設定を一括更新
    """
    try:
        updated_count = 0
        for update in updates:
            if update.visible_for is None or len(update.visible_for) == 0:
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
            updated_count += 1

        db.commit()

        return {
            "success": True,
            "message": f"Updated {updated_count} fields",
            "updated_count": updated_count,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
