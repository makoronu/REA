from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.core.database import get_db
from app.crud.property import property_crud
from app.schemas.property import (
    Property,
    PropertyCreate,
    PropertySearchParams,
    PropertyUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter()


@router.get("/", response_model=List[Property])
def read_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="汎用検索（物件名・物件番号）"),
    sale_price_min: Optional[Decimal] = Query(None, description="最低価格"),
    sale_price_max: Optional[Decimal] = Query(None, description="最高価格"),
    property_type: Optional[str] = Query(None, description="物件種別"),
    property_name: Optional[str] = Query(None, description="物件名"),
    sales_status: Optional[str] = Query(None, description="販売状況"),
    publication_status: Optional[str] = Query(None, description="公開状態"),
    contractor_company_name: Optional[str] = Query(None, description="元請会社名"),
    contractor_contact_person: Optional[str] = Query(None, description="担当者名"),
    contractor_license_number: Optional[str] = Query(None, description="宅建免許番号"),
    sort_by: Optional[str] = Query("id", description="ソート対象カラム"),
    sort_order: Optional[str] = Query("desc", description="ソート順序（asc/desc）"),
    db: Session = Depends(get_db),
):
    """物件一覧取得（検索条件付き）"""
    search_params = PropertySearchParams(
        search=search,
        sale_price_min=sale_price_min,
        sale_price_max=sale_price_max,
        property_type=property_type,
        property_name=property_name,
        sales_status=sales_status,
        publication_status=publication_status,
        contractor_company_name=contractor_company_name,
        contractor_contact_person=contractor_contact_person,
        contractor_license_number=contractor_license_number,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )
    properties = property_crud.get_properties(
        db, skip=skip, limit=limit, search_params=search_params
    )
    return properties


@router.get("/{property_id}", response_model=Property)
def read_property(property_id: int, db: Session = Depends(get_db)):
    """物件詳細取得"""
    db_property = property_crud.get_property(db, property_id=property_id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return db_property


@router.get("/{property_id}/full")
def read_property_full(property_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """物件詳細取得（関連テーブル含む）

    properties, building_info, land_info, amenities を全て含めて返す。
    編集画面で使用する。
    """
    # properties - 直接SQLで取得して確実にデータを取る
    prop_result = db.execute(
        text("SELECT * FROM properties WHERE id = :pid"),
        {"pid": property_id}
    ).fetchone()

    if prop_result is None:
        raise HTTPException(status_code=404, detail="Property not found")

    # propertiesをdictに変換
    result = dict(prop_result._mapping)

    # デバッグ: 住所関連データを出力
    import logging
    logging.warning(f"DEBUG property_id={property_id}: postal_code={result.get('postal_code')}, prefecture={result.get('prefecture')}, city={result.get('city')}, address={result.get('address')}")

    # created_at, updated_atは除外（シリアライズ問題を避ける）
    for key in ['created_at', 'updated_at']:
        if key in result and result[key] is not None:
            result[key] = str(result[key])

    # building_info取得
    building_result = db.execute(
        text("SELECT * FROM building_info WHERE property_id = :pid"),
        {"pid": property_id}
    ).fetchone()
    if building_result:
        building_dict = dict(building_result._mapping)
        # building_info のカラムを直接追加（idとproperty_idは除く）
        for key, value in building_dict.items():
            if key not in ['id', 'property_id', 'created_at', 'updated_at']:
                result[key] = value

    # land_info取得
    land_result = db.execute(
        text("SELECT * FROM land_info WHERE property_id = :pid"),
        {"pid": property_id}
    ).fetchone()
    if land_result:
        land_dict = dict(land_result._mapping)
        # land_info のカラムを直接追加（idとproperty_idは除く）
        for key, value in land_dict.items():
            if key not in ['id', 'property_id', 'created_at', 'updated_at']:
                result[key] = value

    # amenities取得
    amenities_result = db.execute(
        text("SELECT * FROM amenities WHERE property_id = :pid"),
        {"pid": property_id}
    ).fetchone()
    if amenities_result:
        amenities_dict = dict(amenities_result._mapping)
        # amenities のカラムを直接追加（idとproperty_idは除く）
        for key, value in amenities_dict.items():
            if key not in ['id', 'property_id', 'created_at', 'updated_at']:
                result[key] = value

    return result


@router.post("/", response_model=Property)
def create_property(property: PropertyCreate, db: Session = Depends(get_db)):
    """物件新規作成"""
    return property_crud.create_property(db=db, property=property)


@router.put("/{property_id}", response_model=Property)
def update_property(
    property_id: int, property: PropertyUpdate, db: Session = Depends(get_db)
):
    """物件更新"""
    db_property = property_crud.update_property(
        db, property_id=property_id, property_update=property
    )
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return db_property


@router.delete("/{property_id}")
def delete_property(property_id: int, db: Session = Depends(get_db)):
    """物件削除"""
    success = property_crud.delete_property(db, property_id=property_id)
    if not success:
        raise HTTPException(status_code=404, detail="Property not found")
    return {"message": "Property deleted successfully"}


# 元請会社管理専用エンドポイント
@router.get("/by-contractor/{company_name}", response_model=List[Property])
def get_properties_by_contractor(
    company_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """元請会社名で物件を検索"""
    properties = property_crud.get_by_contractor(
        db, company_name=company_name, skip=skip, limit=limit
    )
    return properties


@router.get("/contractors/contacts")
def get_contractor_contacts(db: Session = Depends(get_db)):
    """元請会社の連絡先一覧を取得"""
    contacts = property_crud.get_contractor_contacts(db)
    return contacts
