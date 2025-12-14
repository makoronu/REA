from typing import Any, Dict, List, Optional

from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertySearchParams, PropertyUpdate
from sqlalchemy import func, asc, desc, or_, cast, Integer, case
from sqlalchemy.orm import Session


class PropertyCRUD:
    # ソート可能なカラム
    SORTABLE_COLUMNS = {
        "id": Property.id,
        "property_name": Property.property_name,
        "property_type": Property.property_type,
        "sales_status": Property.sales_status,
        "sale_price": Property.sale_price,  # 既にNUMERIC型
        "created_at": Property.created_at,
        "updated_at": Property.updated_at,
    }

    # テキスト型だが数値としてソートするカラム
    TEXT_TO_NUMERIC_SORT_COLUMNS = {
        "company_property_number": Property.company_property_number,
    }

    def get_properties(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search_params: Optional[PropertySearchParams] = None,
    ) -> List[Property]:
        """物件一覧取得（検索条件付き）"""
        query = db.query(Property)

        if search_params:
            # 汎用検索（物件名・物件番号）
            if search_params.search:
                search_term = f"%{search_params.search}%"
                query = query.filter(
                    or_(
                        Property.property_name.ilike(search_term),
                        Property.company_property_number.ilike(search_term),
                    )
                )

            # 価格範囲
            if search_params.sale_price_min is not None:
                query = query.filter(Property.sale_price >= search_params.sale_price_min)
            if search_params.sale_price_max is not None:
                query = query.filter(Property.sale_price <= search_params.sale_price_max)

            # 物件種別
            if search_params.property_type:
                query = query.filter(Property.property_type.ilike(f"%{search_params.property_type}%"))

            # 物件名検索
            if search_params.property_name:
                query = query.filter(
                    Property.property_name.ilike(f"%{search_params.property_name}%")
                )

            # 販売状況
            if search_params.sales_status:
                query = query.filter(Property.sales_status == search_params.sales_status)

            # 公開状態
            if search_params.publication_status:
                query = query.filter(Property.publication_status == search_params.publication_status)

            # 元請会社検索
            if search_params.contractor_company_name:
                query = query.filter(
                    Property.contractor_company_name.ilike(
                        f"%{search_params.contractor_company_name}%"
                    )
                )
            if search_params.contractor_contact_person:
                query = query.filter(
                    Property.contractor_contact_person.ilike(
                        f"%{search_params.contractor_contact_person}%"
                    )
                )
            if search_params.contractor_license_number:
                query = query.filter(
                    Property.contractor_license_number == search_params.contractor_license_number
                )

            # ソート
            sort_by = search_params.sort_by or "id"

            # テキスト型を数値ソートするカラムの場合
            if sort_by in self.TEXT_TO_NUMERIC_SORT_COLUMNS:
                col = self.TEXT_TO_NUMERIC_SORT_COLUMNS[sort_by]
                # 数値に変換してソート（NULL や非数値は末尾に）
                numeric_col = func.nullif(
                    func.regexp_replace(col, '[^0-9]', '', 'g'),
                    ''
                ).cast(Integer)

                if search_params.sort_order == "asc":
                    query = query.order_by(asc(numeric_col).nullslast())
                else:
                    query = query.order_by(desc(numeric_col).nullsfirst())
            else:
                # 通常のソート
                sort_column = self.SORTABLE_COLUMNS.get(sort_by, Property.id)
                if search_params.sort_order == "asc":
                    query = query.order_by(asc(sort_column))
                else:
                    query = query.order_by(desc(sort_column))
        else:
            # デフォルトソート
            query = query.order_by(desc(Property.id))

        return query.offset(skip).limit(limit).all()

    def get_property(self, db: Session, property_id: int) -> Optional[Property]:
        """物件詳細取得"""
        return db.query(Property).filter(Property.id == property_id).first()

    def create_property(self, db: Session, property: PropertyCreate) -> Property:
        """物件新規作成"""
        db_property = Property(**property.model_dump())
        db.add(db_property)
        db.commit()
        db.refresh(db_property)
        return db_property

    def update_property(
        self, db: Session, property_id: int, property_update: PropertyUpdate
    ) -> Optional[Property]:
        """物件更新"""
        db_property = db.query(Property).filter(Property.id == property_id).first()
        if db_property:
            update_data = property_update.model_dump(exclude_unset=True)
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

    def get_by_contractor(
        self, db: Session, company_name: str, skip: int = 0, limit: int = 100
    ) -> List[Property]:
        """元請会社名で物件を検索"""
        return (
            db.query(Property)
            .filter(Property.contractor_company_name.ilike(f"%{company_name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_contractor_contacts(self, db: Session) -> List[Dict[str, Any]]:
        """元請会社の連絡先一覧を取得"""
        results = (
            db.query(
                Property.contractor_company_name,
                Property.contractor_contact_person,
                Property.contractor_phone,
                Property.contractor_email,
                Property.contractor_address,
                Property.contractor_license_number,
                func.count(Property.id).label("property_count"),
            )
            .filter(Property.contractor_company_name.isnot(None))
            .group_by(
                Property.contractor_company_name,
                Property.contractor_contact_person,
                Property.contractor_phone,
                Property.contractor_email,
                Property.contractor_address,
                Property.contractor_license_number,
            )
            .order_by(Property.contractor_company_name)
            .all()
        )

        return [
            {
                "company_name": result.contractor_company_name,
                "contact_person": result.contractor_contact_person,
                "phone": result.contractor_phone,
                "email": result.contractor_email,
                "address": result.contractor_address,
                "license_number": result.contractor_license_number,
                "property_count": result.property_count,
            }
            for result in results
        ]


# インスタンス作成
property_crud = PropertyCRUD()
