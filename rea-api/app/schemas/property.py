from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel


class PropertyBase(BaseModel):
    # 基本情報
    company_property_number: Optional[str] = None
    external_property_id: Optional[str] = None
    property_name: Optional[str] = None
    property_name_kana: Optional[str] = None
    property_name_public: Optional[str] = None
    property_type: Optional[str] = None
    investment_property: Optional[bool] = False

    # ステータス
    sales_status: Optional[str] = None
    publication_status: Optional[str] = None
    affiliated_group: Optional[str] = None
    priority_score: Optional[int] = None
    property_url: Optional[str] = None

    # 所在地
    postal_code: Optional[str] = None
    prefecture: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    address_detail: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    # 学区・交通
    elementary_school: Optional[str] = None
    elementary_school_minutes: Optional[int] = None
    junior_high_school: Optional[str] = None
    junior_high_school_minutes: Optional[int] = None

    # キャッチコピー・備考
    catch_copy: Optional[str] = None
    catch_copy2: Optional[str] = None
    catch_copy3: Optional[str] = None
    remarks: Optional[str] = None

    # ZOHO連携
    zoho_id: Optional[str] = None
    zoho_synced_at: Optional[datetime] = None
    zoho_sync_status: Optional[str] = None

    # 価格情報
    sale_price: Optional[Decimal] = None
    price_per_tsubo: Optional[Decimal] = None
    price_status: Optional[str] = None
    tax_type: Optional[str] = None

    # 利回り・費用
    yield_rate: Optional[Decimal] = None
    current_yield: Optional[Decimal] = None
    management_fee: Optional[Decimal] = None
    repair_reserve_fund: Optional[Decimal] = None
    repair_reserve_fund_base: Optional[Decimal] = None
    parking_fee: Optional[Decimal] = None
    housing_insurance: Optional[Decimal] = None

    # 入居・引渡し
    current_status: Optional[str] = None
    delivery_date: Optional[str] = None
    delivery_timing: Optional[str] = None
    move_in_consultation: Optional[bool] = False

    # 取引情報
    transaction_type: Optional[str] = None
    brokerage_fee: Optional[Decimal] = None
    commission_split_ratio: Optional[str] = None
    brokerage_contract_date: Optional[datetime] = None
    listing_start_date: Optional[datetime] = None
    listing_confirmation_date: Optional[datetime] = None

    # 元請会社情報
    contractor_company_name: Optional[str] = None
    contractor_contact_person: Optional[str] = None
    contractor_phone: Optional[str] = None
    contractor_email: Optional[str] = None
    contractor_address: Optional[str] = None
    contractor_license_number: Optional[str] = None

    # 管理情報
    property_manager_name: Optional[str] = None
    internal_memo: Optional[str] = None


class PropertyCreate(PropertyBase):
    property_name: str  # 必須


class PropertyUpdate(PropertyBase):
    pass


class PropertyInDBBase(PropertyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Property(PropertyInDBBase):
    pass


class PropertySearchParams(BaseModel):
    search: Optional[str] = None  # 汎用検索（物件名・物件番号）
    sale_price_min: Optional[Decimal] = None
    sale_price_max: Optional[Decimal] = None
    property_type: Optional[str] = None
    property_name: Optional[str] = None
    sales_status: Optional[str] = None
    publication_status: Optional[str] = None
    contractor_company_name: Optional[str] = None
    contractor_contact_person: Optional[str] = None
    contractor_license_number: Optional[str] = None
    sort_by: Optional[str] = "id"  # ソート対象カラム
    sort_order: Optional[str] = "desc"  # asc or desc
    skip: Optional[int] = 0
    limit: Optional[int] = 100
