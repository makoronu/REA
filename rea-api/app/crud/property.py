from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertySearchParams


class PropertyCRUD:
    
    def get_properties(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        search_params: Optional[PropertySearchParams] = None
    ) -> List[Property]:
        """物件一覧取得（検索条件付き）"""
        query = db.query(Property)
        
        if search_params:
            # 価格範囲
            if search_params.price_min is not None:
                query = query.filter(Property.price >= search_params.price_min)
            if search_params.price_max is not None:
                query = query.filter(Property.price <= search_params.price_max)
            
            # 面積範囲
            if search_params.area_min is not None:
                query = query.filter(Property.area_building >= search_params.area_min)
            if search_params.area_max is not None:
                query = query.filter(Property.area_building <= search_params.area_max)
            
            # 物件種別
            if search_params.property_type:
                query = query.filter(Property.property_type == search_params.property_type)
            
            # 地域検索
            if search_params.prefecture:
                query = query.filter(Property.prefecture.ilike(f"%{search_params.prefecture}%"))
            if search_params.city:
                query = query.filter(Property.city.ilike(f"%{search_params.city}%"))
            if search_params.station_name:
                query = query.filter(Property.station_name.ilike(f"%{search_params.station_name}%"))
            
            # 間取り検索
            if search_params.layout:
                query = query.filter(Property.layout.ilike(f"%{search_params.layout}%"))
            
            # 🏢 元請会社検索
            if search_params.contractor_company_name:
                query = query.filter(
                    Property.contractor_company_name.ilike(f"%{search_params.contractor_company_name}%")
                )
            if search_params.contractor_contact_person:
                query = query.filter(
                    Property.contractor_contact_person.ilike(f"%{search_params.contractor_contact_person}%")
                )
            if search_params.contractor_license_number:
                query = query.filter(
                    Property.contractor_license_number == search_params.contractor_license_number
                )
        
        return query.offset(skip).limit(limit).all()

    def get_property(self, db: Session, property_id: int) -> Optional[Property]:
        """物件詳細取得"""
        return db.query(Property).filter(Property.id == property_id).first()

    def get_property_by_homes_id(self, db: Session, homes_id: str) -> Optional[Property]:
        """ホームズIDで物件取得"""
        return db.query(Property).filter(Property.homes_id == homes_id).first()

    def create_property(self, db: Session, property: PropertyCreate) -> Property:
        """物件新規作成"""
        db_property = Property(**property.dict())
        db.add(db_property)
        db.commit()
        db.refresh(db_property)
        return db_property

    def update_property(
        self, 
        db: Session, 
        property_id: int, 
        property_update: PropertyUpdate
    ) -> Optional[Property]:
        """物件更新"""
        db_property = db.query(Property).filter(Property.id == property_id).first()
        if db_property:
            update_data = property_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_property, field, value)
            db.commit()
            db.refresh(db_property)
        return db_property

    def delete_property(self, db: Session, property_id: int) -> bool:
        """物件削除"""
        db_property = db.query(Property).filter(Property.id == property_id).first()
        if db_property:
            db.delete(db_property)
            db.commit()
            return True
        return False

    def deactivate_property(self, db: Session, property_id: int) -> Optional[Property]:
        """物件非表示"""
        db_property = db.query(Property).filter(Property.id == property_id).first()
        if db_property:
            db_property.is_active = False
            db.commit()
            db.refresh(db_property)
        return db_property

    def get_by_contractor(
        self, 
        db: Session, 
        company_name: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Property]:
        """元請会社名で物件を検索"""
        return db.query(Property).filter(
            Property.contractor_company_name.ilike(f"%{company_name}%"),
            Property.is_active == True
        ).offset(skip).limit(limit).all()

    def get_contractor_contacts(self, db: Session) -> List[Dict[str, Any]]:
        """元請会社の連絡先一覧を取得"""
        results = db.query(
            Property.contractor_company_name,
            Property.contractor_contact_person,
            Property.contractor_phone,
            Property.contractor_email,
            Property.contractor_address,
            Property.contractor_license_number,
            func.count(Property.id).label('property_count')
        ).filter(
            Property.contractor_company_name.isnot(None),
            Property.is_active == True
        ).group_by(
            Property.contractor_company_name,
            Property.contractor_contact_person,
            Property.contractor_phone,
            Property.contractor_email,
            Property.contractor_address,
            Property.contractor_license_number
        ).order_by(
            Property.contractor_company_name
        ).all()

        return [
            {
                "company_name": result.contractor_company_name,
                "contact_person": result.contractor_contact_person,
                "phone": result.contractor_phone,
                "email": result.contractor_email,
                "address": result.contractor_address,
                "license_number": result.contractor_license_number,
                "property_count": result.property_count
            }
            for result in results
        ]


# インスタンス作成
property_crud = PropertyCRUD()