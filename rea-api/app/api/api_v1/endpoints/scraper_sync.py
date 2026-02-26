"""
スクレイパー同期API — MI scraper → REA bulk upsert

ContaboのMI scraperから送信されたデータを
rea_scraperのproperties / land_info / building_info にUPSERTする。
"""
import logging
from typing import Any, Dict, List

from app.core.database import get_db
from app.crud.generic import GenericCRUD
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from shared.auth.middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


def _require_auth(request: Request) -> dict:
    """認証を要求"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="認証が必要です")
    return user


# フィールド振り分け定数
_LAND_INFO_KEYS = frozenset({
    "postal_code", "prefecture", "city", "address", "latitude", "longitude",
    "land_area", "land_category", "use_district", "city_planning",
    "building_coverage_ratio", "floor_area_ratio",
})
_BUILDING_INFO_KEYS = frozenset({
    "building_structure", "construction_date", "building_area",
    "total_floor_area", "room_count", "room_type", "total_units",
})
_SKIP_KEYS = frozenset({"property_url"})


@router.post("/bulk-upsert", response_model=Dict[str, Any])
def bulk_upsert_properties(
    request: Request,
    items: List[Dict[str, Any]],
    db: Session = Depends(get_db),
):
    """
    物件一括UPSERT（MI scraper → REA同期用）

    property_urlをユニークキーとしてUPSERT。
    各itemは properties / land_info / building_info のフィールドを含む。
    1物件ずつトランザクション（部分成功許容）。
    """
    user = _require_auth(request)
    organization_id = user["organization_id"]

    stats = {"created": 0, "updated": 0, "errors": []}

    for idx, item in enumerate(items):
        try:
            result = _upsert_one_property(db, item, organization_id)
            stats[result] += 1
        except Exception as e:
            logger.error(f"bulk-upsert item[{idx}] failed: {e}")
            db.rollback()
            stats["errors"].append({"index": idx, "detail": str(e)})

    return stats


def _upsert_one_property(
    db: Session, item: Dict[str, Any], organization_id: int
) -> str:
    """1物件をUPSERT。'created' or 'updated' を返す。"""
    property_url = item.get("property_url")
    if not property_url:
        raise ValueError("property_url is required")

    # 既存チェック
    result = db.execute(
        text("SELECT id FROM properties WHERE property_url = :url AND deleted_at IS NULL"),
        {"url": property_url},
    )
    existing = result.fetchone()

    crud = GenericCRUD(db)

    props_data = {}
    land_data = {}
    building_data = {}

    for key, val in item.items():
        if val is None or key in _SKIP_KEYS:
            continue
        if key in _LAND_INFO_KEYS:
            land_data[key] = val
        elif key in _BUILDING_INFO_KEYS:
            building_data[key] = val
        else:
            props_data[key] = val

    if existing:
        property_id = existing[0]
        if props_data:
            crud.update("properties", property_id, props_data, commit=False)
        if land_data:
            _upsert_related_table(db, "land_info", property_id, land_data)
        if building_data:
            _upsert_related_table(db, "building_info", property_id, building_data)
        db.commit()
        return "updated"
    else:
        props_data["property_url"] = property_url
        if not props_data.get("property_name"):
            props_data["property_name"] = "（スクレイピング物件）"
        new_prop = crud.create("properties", props_data, extra_fields={
            "organization_id": organization_id,
        }, commit=False)
        property_id = new_prop["id"]
        if land_data:
            _upsert_related_table(db, "land_info", property_id, land_data)
        if building_data:
            _upsert_related_table(db, "building_info", property_id, building_data)
        db.commit()
        return "created"


def _upsert_related_table(
    db: Session, table_name: str, property_id: int, data: Dict[str, Any]
):
    """関連テーブル（land_info / building_info）にUPSERT"""
    if table_name not in ("land_info", "building_info"):
        raise ValueError(f"Invalid table: {table_name}")

    result = db.execute(
        text(f"SELECT id FROM {table_name} WHERE property_id = :pid AND deleted_at IS NULL"),
        {"pid": property_id},
    )
    existing = result.fetchone()

    if existing:
        set_parts = ["updated_at = NOW()"]
        params = {"rid": existing[0]}
        for i, (col, val) in enumerate(data.items()):
            param_key = f"v{i}"
            set_parts.append(f"{col} = :{param_key}")
            params[param_key] = val
        db.execute(
            text(f"UPDATE {table_name} SET {', '.join(set_parts)} WHERE id = :rid AND deleted_at IS NULL"),
            params,
        )
    else:
        columns = ["property_id", "created_at", "updated_at"]
        params = {"pid": property_id}
        for i, (col, val) in enumerate(data.items()):
            param_key = f"v{i}"
            columns.append(col)
            params[param_key] = val
        col_names = ", ".join(columns)
        placeholders = ":pid, NOW(), NOW(), " + ", ".join(f":v{i}" for i in range(len(data)))
        db.execute(
            text(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"),
            params,
        )
