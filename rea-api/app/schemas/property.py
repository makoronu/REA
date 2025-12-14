# app/schemas/property.py
"""
物件スキーマ - 最小限の定義のみ

メタデータ駆動に移行したため、Pydanticスキーマは最小限に。
APIレスポンスは Dict[str, Any] を使用する。

検索パラメータなど、一部の機能のみ残している。
"""
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel


class PropertySearchParams(BaseModel):
    """検索パラメータ（後方互換性のため）"""
    search: Optional[str] = None
    sale_price_min: Optional[Decimal] = None
    sale_price_max: Optional[Decimal] = None
    property_type: Optional[str] = None
    property_name: Optional[str] = None
    sales_status: Optional[str] = None
    publication_status: Optional[str] = None
    sort_by: Optional[str] = "id"
    sort_order: Optional[str] = "desc"
    skip: Optional[int] = 0
    limit: Optional[int] = 100


# NOTE: PropertyBase, PropertyCreate, PropertyUpdate, Property は削除。
# メタデータ駆動では Dict[str, Any] を使用する。
# カラム定義は column_labels テーブルで管理する。
