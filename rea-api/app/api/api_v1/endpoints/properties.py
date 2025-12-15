"""
物件API - メタデータ駆動版

全てのCRUD操作はGenericCRUDを使用し、
column_labelsテーブルをベースに動的に処理する。
ハードコードなし。
"""
import logging
from typing import Any, Dict, List, Optional

from app.core.database import get_db
from app.crud.generic import GenericCRUD
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
def read_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="汎用検索（物件名・物件番号）"),
    property_type: Optional[str] = Query(None, description="物件種別"),
    sales_status: Optional[str] = Query(None, description="販売状況"),
    publication_status: Optional[str] = Query(None, description="公開状態"),
    sort_by: Optional[str] = Query("id", description="ソート対象カラム"),
    sort_order: Optional[str] = Query("desc", description="ソート順序（asc/desc）"),
    db: Session = Depends(get_db),
):
    """
    物件一覧取得（検索条件付き）
    メタデータ駆動: フィルタ条件は動的に構築
    """
    crud = GenericCRUD(db)

    # フィルタ条件を構築
    filters: Dict[str, Any] = {}
    if property_type:
        filters["property_type"] = f"%{property_type}%"
    if sales_status:
        filters["sales_status"] = sales_status
    if publication_status:
        filters["publication_status"] = publication_status

    # 汎用検索
    if search:
        # 検索は別メソッドで処理
        results = crud.search(
            "properties",
            search,
            search_columns=["property_name", "company_property_number"],
            skip=skip,
            limit=limit,
        )
    else:
        results = crud.get_list(
            "properties",
            skip=skip,
            limit=limit,
            filters=filters if filters else None,
            sort_by=sort_by or "id",
            sort_order=sort_order or "desc",
        )

    return results


@router.get("/{property_id}", response_model=Dict[str, Any])
def read_property(property_id: int, db: Session = Depends(get_db)):
    """
    物件詳細取得（propertiesテーブルのみ）
    """
    crud = GenericCRUD(db)
    result = crud.get("properties", property_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Property not found")

    return result


@router.get("/{property_id}/full", response_model=Dict[str, Any])
def read_property_full(property_id: int, db: Session = Depends(get_db)):
    """
    物件詳細取得（関連テーブル含む）
    メタデータ駆動: 重複カラムはpropertiesを優先

    properties, building_info, land_info, amenities を全て含めて返す。
    編集画面で使用する。
    """
    crud = GenericCRUD(db)
    result = crud.get_full(property_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Property not found")

    return result


@router.post("/", response_model=Dict[str, Any])
def create_property(property_data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    物件新規作成
    メタデータ駆動: 有効なカラムのみ受け付け
    """
    crud = GenericCRUD(db)

    # property_nameは必須
    if not property_data.get("property_name"):
        raise HTTPException(status_code=400, detail="property_name is required")

    try:
        result = crud.create("properties", property_data)
        return result
    except ValueError as e:
        logger.error(f"Validation error creating property: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating property: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"データベースエラー: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating property: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"予期せぬエラー: {str(e)}"
        )


@router.put("/{property_id}", response_model=Dict[str, Any])
def update_property(
    property_id: int,
    property_data: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """
    物件更新（全テーブル対応）
    メタデータ駆動: データを適切なテーブルに振り分け
    """
    crud = GenericCRUD(db)

    # 存在確認
    existing = crud.get("properties", property_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Property not found")

    try:
        result = crud.update_full(property_id, property_data)
        return result
    except ValueError as e:
        logger.error(f"Validation error updating property {property_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error updating property {property_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"データベースエラー: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating property {property_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"予期せぬエラー: {str(e)}"
        )


@router.delete("/{property_id}")
def delete_property(property_id: int, db: Session = Depends(get_db)):
    """
    物件削除
    関連テーブルも削除
    """
    crud = GenericCRUD(db)

    # 存在確認
    existing = crud.get("properties", property_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Property not found")

    # 関連テーブルを先に削除（アプリ層で明示的に削除制御）
    for table_name in ["building_info", "land_info", "amenities", "property_images", "property_locations"]:
        db.execute(
            text(f"DELETE FROM {table_name} WHERE property_id = :pid"),
            {"pid": property_id}
        )

    # properties を削除
    success = crud.delete("properties", property_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete property")

    return {"message": "Property deleted successfully"}


# === 元請会社管理 ===
# これらはメタデータ駆動とは別の集計機能

@router.get("/contractors/contacts")
def get_contractor_contacts(db: Session = Depends(get_db)):
    """元請会社の連絡先一覧を取得"""
    result = db.execute(text("""
        SELECT
            contractor_company_name,
            contractor_contact_person,
            contractor_phone,
            contractor_email,
            contractor_address,
            contractor_license_number,
            COUNT(id) as property_count
        FROM properties
        WHERE contractor_company_name IS NOT NULL
        GROUP BY
            contractor_company_name,
            contractor_contact_person,
            contractor_phone,
            contractor_email,
            contractor_address,
            contractor_license_number
        ORDER BY contractor_company_name
    """))

    return [
        {
            "company_name": row.contractor_company_name,
            "contact_person": row.contractor_contact_person,
            "phone": row.contractor_phone,
            "email": row.contractor_email,
            "address": row.contractor_address,
            "license_number": row.contractor_license_number,
            "property_count": row.property_count,
        }
        for row in result
    ]
