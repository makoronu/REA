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
    """単一のフィールド表示設定を更新（共通処理）"""
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
