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
from app.services.publication_validator import (
    validate_for_publication,
    format_validation_error,
    format_validation_error_grouped,
)
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from shared.auth.middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


def require_auth(request: Request) -> dict:
    """認証を要求（ログイン必須）"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="認証が必要です")
    return user


@router.get("/", response_model=List[Dict[str, Any]])
def read_properties(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="汎用検索（物件名・物件番号）"),
    property_type: Optional[str] = Query(None, description="物件種別"),
    sales_status: Optional[str] = Query(None, description="販売状況"),
    publication_status: Optional[str] = Query(None, description="公開状態"),
    sale_price_min: Optional[int] = Query(None, description="最低価格（円）"),
    sale_price_max: Optional[int] = Query(None, description="最高価格（円）"),
    sort_by: Optional[str] = Query("id", description="ソート対象カラム"),
    sort_order: Optional[str] = Query("desc", description="ソート順序（asc/desc）"),
    db: Session = Depends(get_db),
):
    """
    物件一覧取得（検索条件付き）
    メタデータ駆動: フィルタ条件は動的に構築
    """
    require_auth(request)
    crud = GenericCRUD(db)

    # フィルタ条件を構築
    filters: Dict[str, Any] = {}
    if property_type:
        filters["property_type"] = f"%{property_type}%"
    if sales_status:
        filters["sales_status"] = sales_status
    if publication_status:
        filters["publication_status"] = publication_status

    # 価格範囲フィルタ
    range_filters: Dict[str, Any] = {}
    if sale_price_min is not None:
        range_filters["sale_price__gte"] = sale_price_min
    if sale_price_max is not None:
        range_filters["sale_price__lte"] = sale_price_max

    # 汎用検索
    if search:
        # 検索は別メソッドで処理
        results = crud.search(
            "properties",
            search,
            search_columns=["property_name", "company_property_number"],
            skip=skip,
            limit=limit,
            range_filters=range_filters if range_filters else None,
        )
    else:
        results = crud.get_list(
            "properties",
            skip=skip,
            limit=limit,
            filters=filters if filters else None,
            range_filters=range_filters if range_filters else None,
            sort_by=sort_by or "id",
            sort_order=sort_order or "desc",
        )

    return results


@router.get("/{property_id}", response_model=Dict[str, Any])
def read_property(request: Request, property_id: int, db: Session = Depends(get_db)):
    """
    物件詳細取得（propertiesテーブルのみ）
    """
    require_auth(request)
    crud = GenericCRUD(db)
    result = crud.get("properties", property_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Property not found")

    return result


@router.get("/{property_id}/full", response_model=Dict[str, Any])
def read_property_full(request: Request, property_id: int, db: Session = Depends(get_db)):
    """
    物件詳細取得（関連テーブル含む）
    メタデータ駆動: 重複カラムはpropertiesを優先

    properties, building_info, land_info, amenities を全て含めて返す。
    編集画面で使用する。
    """
    require_auth(request)
    crud = GenericCRUD(db)
    result = crud.get_full(property_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Property not found")

    return result


@router.post("/", response_model=Dict[str, Any])
def create_property(request: Request, property_data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    物件新規作成
    メタデータ駆動: 有効なカラムのみ受け付け
    """
    require_auth(request)
    crud = GenericCRUD(db)

    # 文字列フィールドのトリム処理
    for key, value in property_data.items():
        if isinstance(value, str):
            property_data[key] = value.strip()

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
    request: Request,
    property_id: int,
    property_data: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """
    物件更新（全テーブル対応）
    メタデータ駆動: データを適切なテーブルに振り分け

    公開時バリデーション:
    publication_statusが「公開」「会員公開」に変更される場合、
    required_for_publicationで設定された必須項目をチェック
    """
    require_auth(request)
    crud = GenericCRUD(db)

    # 文字列フィールドのトリム処理
    for key, value in property_data.items():
        if isinstance(value, str):
            property_data[key] = value.strip()

    # property_nameがnullの場合は400エラー
    if "property_name" in property_data and property_data["property_name"] is None:
        raise HTTPException(status_code=400, detail="property_nameをnullにすることはできません")

    # publication_statusがnullの場合は400エラー
    if "publication_status" in property_data and property_data["publication_status"] is None:
        raise HTTPException(status_code=400, detail="publication_statusをnullにすることはできません")

    # publication_statusの値バリデーション
    VALID_PUBLICATION_STATUSES = ["公開", "非公開", "会員公開"]
    if "publication_status" in property_data and property_data["publication_status"] is not None:
        if property_data["publication_status"] not in VALID_PUBLICATION_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"publication_statusの値が不正です。有効な値: {', '.join(VALID_PUBLICATION_STATUSES)}"
            )

    # 存在確認 & 現在データ取得（全テーブル）
    existing_full = crud.get_full(property_id)
    if existing_full is None:
        raise HTTPException(status_code=404, detail="Property not found")

    # 公開時バリデーション
    new_publication_status = property_data.get("publication_status")
    if new_publication_status:
        # 現在データと更新データをマージ
        merged_data = {**existing_full, **property_data}
        current_status = existing_full.get("publication_status")

        is_valid, missing_fields = validate_for_publication(
            db, merged_data, new_publication_status, current_status
        )
        if not is_valid:
            # 詳細なエラー情報を返す（グループ別）
            error_detail = format_validation_error_grouped(missing_fields, new_publication_status)
            raise HTTPException(status_code=400, detail=error_detail)

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
def delete_property(request: Request, property_id: int, db: Session = Depends(get_db)):
    """
    物件論理削除
    関連テーブルも論理削除
    """
    require_auth(request)
    crud = GenericCRUD(db)

    # 存在確認
    existing = crud.get("properties", property_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Property not found")

    # 関連テーブルを先に論理削除（deleted_atを設定）
    for table_name in ["building_info", "land_info", "property_images", "property_registries"]:
        db.execute(
            text(f"UPDATE {table_name} SET deleted_at = NOW() WHERE property_id = :pid AND deleted_at IS NULL"),
            {"pid": property_id}
        )

    # properties を論理削除
    success = crud.delete("properties", property_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete property")

    return {"message": "Property deleted successfully"}


# === 元請会社管理 ===
# これらはメタデータ駆動とは別の集計機能

@router.get("/contractors/contacts")
def get_contractor_contacts(request: Request, db: Session = Depends(get_db)):
    """元請会社の連絡先一覧を取得"""
    require_auth(request)
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
