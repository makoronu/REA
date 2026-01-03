# テーブル名定数
# SQLインジェクション対策のホワイトリスト
# 全てのテーブル名はここで一元管理する

from typing import Set

# 物件関連テーブル（CRUD操作対象）
PROPERTY_TABLES: Set[str] = {
    "properties",
    "building_info",
    "land_info",
    "property_images",
    "property_locations",
    "property_registries",
    "amenities",
}

# メタデータテーブル（管理画面で参照）
METADATA_TABLES: Set[str] = {
    "column_labels",
    "master_categories",
    "master_options",
}

# マスタテーブル（参照のみ）
MASTER_TABLES: Set[str] = {
    "m_facilities",
    "m_stations",
    "m_postal_codes",
    "m_roles",
}

# 全許可テーブル（metadata API用）
ALL_ALLOWED_TABLES: Set[str] = PROPERTY_TABLES | METADATA_TABLES | MASTER_TABLES

# GenericCRUD用（CRUD操作を許可するテーブル）
CRUD_ALLOWED_TABLES: Set[str] = PROPERTY_TABLES
