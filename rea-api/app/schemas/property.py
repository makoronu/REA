from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, validator


class PropertyBase(BaseModel):
    title: str
    price: float
    price_unit: Optional[str] = "その他"
    contractor_company_name: Optional[str] = None
    contractor_contact_person: Optional[str] = None
    contractor_phone: Optional[str] = None
    contractor_email: Optional[str] = None
    contractor_address: Optional[str] = None
    contractor_license_number: Optional[str] = None
    property_type: Optional[str] = None
    building_structure: Optional[str] = None
    floors_total: Optional[int] = None
    floor_current: Optional[int] = None
    area_building: Optional[float] = None
    area_land: Optional[float] = None
    layout: Optional[str] = None
    rooms: Optional[int] = None
    built_year: Optional[int] = None
    station_name: Optional[str] = None
    station_walk_time: Optional[int] = None
    station_line: Optional[str] = None
    prefecture: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    equipments: Optional[List[str]] = []
    images: Optional[List[str]] = []
    homes_id: Optional[str] = None
    homes_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True
    source: Optional[str] = "homes"


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(PropertyBase):
    title: Optional[str] = None
    price: Optional[float] = None


class PropertyInDBBase(PropertyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Property(PropertyInDBBase):
    pass


class PropertySearchParams(BaseModel):
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    property_type: Optional[str] = None
    prefecture: Optional[str] = None
    city: Optional[str] = None
    station_name: Optional[str] = None
    layout: Optional[str] = None
    area_min: Optional[float] = None
    area_max: Optional[float] = None
    contractor_company_name: Optional[str] = None
    contractor_contact_person: Optional[str] = None
    contractor_license_number: Optional[str] = None
    skip: Optional[int] = 0
    limit: Optional[int] = 100
