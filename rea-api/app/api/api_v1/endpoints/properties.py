from typing import List, Optional

from app.core.database import get_db
from app.crud import property as property_crud
from app.schemas.property import (
    Property,
    PropertyCreate,
    PropertySearchParams,
    PropertyUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[Property])
def read_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    area_min: Optional[float] = Query(None),
    area_max: Optional[float] = Query(None),
    property_type: Optional[str] = Query(None),
    prefecture: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    station_name: Optional[str] = Query(None),
    layout: Optional[str] = Query(None),
    # 🏢 元請会社検索パラメータ（新規追加）
    contractor_company_name: Optional[str] = Query(None, description="元請会社名"),
    contractor_contact_person: Optional[str] = Query(None, description="担当者名"),
    contractor_license_number: Optional[str] = Query(None, description="宅建免許番号"),
    db: Session = Depends(get_db),
):
    """物件一覧取得（検索条件付き）"""
    search_params = PropertySearchParams(
        price_min=price_min,
        price_max=price_max,
        area_min=area_min,
        area_max=area_max,
        property_type=property_type,
        prefecture=prefecture,
        city=city,
        station_name=station_name,
        layout=layout,
        contractor_company_name=contractor_company_name,
        contractor_contact_person=contractor_contact_person,
        contractor_license_number=contractor_license_number,
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


@router.post("/", response_model=Property)
def create_property(property: PropertyCreate, db: Session = Depends(get_db)):
    """物件新規作成"""
    # ホームズIDの重複チェック
    if property.homes_id:
        existing_property = property_crud.get_property_by_homes_id(
            db, homes_id=property.homes_id
        )
        if existing_property:
            raise HTTPException(
                status_code=400, detail="Property with this homes_id already exists"
            )

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


@router.patch("/{property_id}/deactivate", response_model=Property)
def deactivate_property(property_id: int, db: Session = Depends(get_db)):
    """物件非表示"""
    db_property = property_crud.deactivate_property(db, property_id=property_id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return db_property


# 🏢 元請会社管理専用エンドポイント
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
