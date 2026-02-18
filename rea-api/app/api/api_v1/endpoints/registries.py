"""
登記情報API

property_registries（表題部）+ registry_kou_entries（甲区）+ registry_otsu_entries（乙区）
実務書類（重要事項説明書、売買契約書、登記申請書）に必要な項目を網羅
"""
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from shared.database import READatabase

router = APIRouter()


# ====================
# 甲区（所有権）スキーマ
# ====================
class KouEntryCreate(BaseModel):
    rank_number: str
    purpose: str
    reception_date: Optional[str] = None
    reception_number: Optional[str] = None
    owner_name: str
    owner_address: Optional[str] = None
    ownership_ratio: Optional[str] = None
    cause: Optional[str] = None
    cause_date: Optional[str] = None
    cause_detail: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None


class KouEntryResponse(BaseModel):
    id: int
    registry_id: int
    rank_number: str
    purpose: str
    reception_date: Optional[str] = None
    reception_number: Optional[str] = None
    owner_name: str
    owner_address: Optional[str] = None
    ownership_ratio: Optional[str] = None
    cause: Optional[str] = None
    cause_date: Optional[str] = None
    cause_detail: Optional[str] = None
    is_active: bool
    deletion_date: Optional[str] = None
    deletion_reception_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ====================
# 乙区（抵当権等）スキーマ
# ====================
class OtsuEntryCreate(BaseModel):
    rank_number: str
    purpose: str
    reception_date: Optional[str] = None
    reception_number: Optional[str] = None
    debt_amount: Optional[int] = None
    interest_rate: Optional[str] = None
    damage_rate: Optional[str] = None
    debtor_name: Optional[str] = None
    debtor_address: Optional[str] = None
    mortgagee_name: Optional[str] = None
    mortgagee_address: Optional[str] = None
    maximum_amount: Optional[int] = None
    debt_scope: Optional[str] = None
    right_holder_name: Optional[str] = None
    right_holder_address: Optional[str] = None
    right_purpose: Optional[str] = None
    right_scope: Optional[str] = None
    right_duration: Optional[str] = None
    rent_amount: Optional[str] = None
    cause: Optional[str] = None
    cause_date: Optional[str] = None
    joint_collateral_number: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None


class OtsuEntryResponse(BaseModel):
    id: int
    registry_id: int
    rank_number: str
    purpose: str
    reception_date: Optional[str] = None
    reception_number: Optional[str] = None
    debt_amount: Optional[int] = None
    interest_rate: Optional[str] = None
    damage_rate: Optional[str] = None
    debtor_name: Optional[str] = None
    debtor_address: Optional[str] = None
    mortgagee_name: Optional[str] = None
    mortgagee_address: Optional[str] = None
    maximum_amount: Optional[int] = None
    debt_scope: Optional[str] = None
    right_holder_name: Optional[str] = None
    right_holder_address: Optional[str] = None
    right_purpose: Optional[str] = None
    right_scope: Optional[str] = None
    right_duration: Optional[str] = None
    rent_amount: Optional[str] = None
    cause: Optional[str] = None
    cause_date: Optional[str] = None
    joint_collateral_number: Optional[str] = None
    is_active: bool
    deletion_date: Optional[str] = None
    deletion_reception_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegistryResponse(BaseModel):
    id: int
    property_id: int
    registry_type: str
    location: Optional[str] = None
    chiban: Optional[str] = None
    land_category: Optional[str] = None
    land_area: Optional[float] = None
    building_number: Optional[str] = None
    building_type: Optional[str] = None
    building_structure: Optional[str] = None
    floor_area_1f: Optional[float] = None
    floor_area_2f: Optional[float] = None
    floor_area_3f: Optional[float] = None
    floor_area_total: Optional[float] = None
    built_date: Optional[str] = None
    owner_name: Optional[str] = None
    owner_address: Optional[str] = None
    ownership_ratio: Optional[str] = None
    ownership_cause: Optional[str] = None
    ownership_date: Optional[str] = None
    mortgage_holder: Optional[str] = None
    mortgage_amount: Optional[int] = None
    mortgage_date: Optional[str] = None
    other_rights: Optional[dict] = None
    registration_number: Optional[str] = None
    registry_office: Optional[str] = None
    certified_date: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegistryListResponse(BaseModel):
    items: List[RegistryResponse]
    total: int


class RegistryCreate(BaseModel):
    registry_type: str  # 土地 / 建物
    location: Optional[str] = None
    chiban: Optional[str] = None
    land_category: Optional[str] = None
    land_area: Optional[float] = None
    building_number: Optional[str] = None
    building_type: Optional[str] = None
    building_structure: Optional[str] = None
    floor_area_1f: Optional[float] = None
    floor_area_2f: Optional[float] = None
    floor_area_3f: Optional[float] = None
    floor_area_total: Optional[float] = None
    built_date: Optional[str] = None
    owner_name: Optional[str] = None
    owner_address: Optional[str] = None
    ownership_ratio: Optional[str] = None
    ownership_cause: Optional[str] = None
    ownership_date: Optional[str] = None
    mortgage_holder: Optional[str] = None
    mortgage_amount: Optional[int] = None
    mortgage_date: Optional[str] = None
    other_rights: Optional[dict] = None
    registration_number: Optional[str] = None
    registry_office: Optional[str] = None
    certified_date: Optional[str] = None
    notes: Optional[str] = None


class RegistryUpdate(BaseModel):
    registry_type: Optional[str] = None
    location: Optional[str] = None
    chiban: Optional[str] = None
    land_category: Optional[str] = None
    land_area: Optional[float] = None
    building_number: Optional[str] = None
    building_type: Optional[str] = None
    building_structure: Optional[str] = None
    floor_area_1f: Optional[float] = None
    floor_area_2f: Optional[float] = None
    floor_area_3f: Optional[float] = None
    floor_area_total: Optional[float] = None
    built_date: Optional[str] = None
    owner_name: Optional[str] = None
    owner_address: Optional[str] = None
    ownership_ratio: Optional[str] = None
    ownership_cause: Optional[str] = None
    ownership_date: Optional[str] = None
    mortgage_holder: Optional[str] = None
    mortgage_amount: Optional[int] = None
    mortgage_date: Optional[str] = None
    other_rights: Optional[dict] = None
    registration_number: Optional[str] = None
    registry_office: Optional[str] = None
    certified_date: Optional[str] = None
    notes: Optional[str] = None


def row_to_dict(row, columns) -> dict:
    """DBの行を辞書に変換"""
    return {col: row[i] for i, col in enumerate(columns)}


# カラム一覧（selectで使う）
REGISTRY_COLUMNS = [
    'id', 'property_id', 'registry_type', 'location', 'chiban',
    'land_category', 'land_area', 'building_number', 'building_type',
    'building_structure', 'floor_area_1f', 'floor_area_2f', 'floor_area_3f',
    'floor_area_total', 'built_date', 'owner_name', 'owner_address',
    'ownership_ratio', 'ownership_cause', 'ownership_date',
    'mortgage_holder', 'mortgage_amount', 'mortgage_date', 'other_rights',
    'registration_number', 'registry_office', 'certified_date', 'notes',
    'created_at', 'updated_at'
]


# ====================
# 静的パス（{registry_id}より先に定義）
# ====================
@router.get("/registries/purposes")
async def get_registry_purposes():
    """登記目的マスター取得"""
    with READatabase.cursor() as (cur, conn):
        cur.execute("""
            SELECT id, section, code, name, description, display_order
            FROM m_registry_purposes
            WHERE is_active = TRUE
            ORDER BY section, display_order
        """)
        rows = cur.fetchall()

        result = {"甲区": [], "乙区": []}
        for row in rows:
            entry = {
                "id": row[0],
                "code": row[2],
                "name": row[3],
                "description": row[4]
            }
            result[row[1]].append(entry)

        return result


@router.get("/registries/metadata")
async def get_registry_metadata():
    """登記情報のメタデータ（column_labelsから取得）"""
    with READatabase.cursor() as (cur, conn):
        cur.execute("""
            SELECT column_name, japanese_label, input_type, group_name,
                   is_required, description, master_category_code
            FROM column_labels
            WHERE table_name = 'property_registries'
            AND group_name NOT IN ('システム')
            ORDER BY display_order
        """)
        rows = cur.fetchall()

        columns = []
        for row in rows:
            columns.append({
                'name': row[0],
                'label': row[1],
                'type': row[2] or 'text',
                'group': row[3],
                'required': row[4] or False,
                'description': row[5],
                'master_category_code': row[6]
            })

        # グループ別に整理
        groups = {}
        for col in columns:
            group = col['group'] or 'その他'
            if group not in groups:
                groups[group] = []
            groups[group].append(col)

        return {
            'columns': columns,
            'groups': groups
        }


@router.get("/properties/{property_id}/registries", response_model=RegistryListResponse)
async def get_property_registries(property_id: int):
    """物件の登記情報一覧を取得"""
    with READatabase.cursor() as (cur, conn):
        # 物件存在確認
        cur.execute("SELECT id FROM properties WHERE id = %s AND deleted_at IS NULL", (property_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="物件が見つかりません")

        # 登記一覧取得
        cur.execute(f"""
            SELECT {', '.join(REGISTRY_COLUMNS)}
            FROM property_registries
            WHERE property_id = %s AND deleted_at IS NULL
            ORDER BY registry_type, id
        """, (property_id,))
        rows = cur.fetchall()

        items = []
        for row in rows:
            data = row_to_dict(row, REGISTRY_COLUMNS)
            # 日付をstr変換
            for key in ['built_date', 'ownership_date', 'mortgage_date', 'certified_date']:
                if data.get(key):
                    data[key] = str(data[key])
            items.append(RegistryResponse(**data))

        return RegistryListResponse(items=items, total=len(items))


@router.post("/properties/{property_id}/registries", response_model=RegistryResponse)
async def create_registry(property_id: int, data: RegistryCreate):
    """登記情報を追加"""
    with READatabase.cursor(commit=True) as (cur, conn):
        # 物件存在確認
        cur.execute("SELECT id FROM properties WHERE id = %s AND deleted_at IS NULL", (property_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="物件が見つかりません")

        # データ準備
        insert_data = data.model_dump(exclude_none=True)
        insert_data['property_id'] = property_id

        columns = list(insert_data.keys())
        values = [insert_data[col] for col in columns]
        placeholders = ', '.join(['%s'] * len(columns))

        cur.execute(f"""
            INSERT INTO property_registries ({', '.join(columns)})
            VALUES ({placeholders})
            RETURNING {', '.join(REGISTRY_COLUMNS)}
        """, values)

        row = cur.fetchone()
        result = row_to_dict(row, REGISTRY_COLUMNS)

        # 日付をstr変換
        for key in ['built_date', 'ownership_date', 'mortgage_date', 'certified_date']:
            if result.get(key):
                result[key] = str(result[key])

        return RegistryResponse(**result)


@router.get("/registries/{registry_id}", response_model=RegistryResponse)
async def get_registry(registry_id: int):
    """登記情報詳細を取得"""
    with READatabase.cursor() as (cur, conn):
        cur.execute(f"""
            SELECT {', '.join(REGISTRY_COLUMNS)}
            FROM property_registries
            WHERE id = %s AND deleted_at IS NULL
        """, (registry_id,))

        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="登記情報が見つかりません")

        result = row_to_dict(row, REGISTRY_COLUMNS)

        # 日付をstr変換
        for key in ['built_date', 'ownership_date', 'mortgage_date', 'certified_date']:
            if result.get(key):
                result[key] = str(result[key])

        return RegistryResponse(**result)


@router.put("/registries/{registry_id}", response_model=RegistryResponse)
async def update_registry(registry_id: int, data: RegistryUpdate):
    """登記情報を更新"""
    with READatabase.cursor(commit=True) as (cur, conn):
        # 存在確認
        cur.execute("SELECT id FROM property_registries WHERE id = %s AND deleted_at IS NULL", (registry_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="登記情報が見つかりません")

        # 更新データ準備
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="更新データがありません")

        set_clauses = [f"{col} = %s" for col in update_data.keys()]
        values = list(update_data.values())
        values.append(registry_id)

        cur.execute(f"""
            UPDATE property_registries
            SET {', '.join(set_clauses)}, updated_at = NOW()
            WHERE id = %s AND deleted_at IS NULL
            RETURNING {', '.join(REGISTRY_COLUMNS)}
        """, values)

        row = cur.fetchone()
        result = row_to_dict(row, REGISTRY_COLUMNS)

        # 日付をstr変換
        for key in ['built_date', 'ownership_date', 'mortgage_date', 'certified_date']:
            if result.get(key):
                result[key] = str(result[key])

        return RegistryResponse(**result)


@router.delete("/registries/{registry_id}")
async def delete_registry(registry_id: int):
    """登記情報を論理削除"""
    with READatabase.cursor(commit=True) as (cur, conn):
        cur.execute(
            "UPDATE property_registries SET deleted_at = NOW() WHERE id = %s AND deleted_at IS NULL RETURNING id",
            (registry_id,)
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="登記情報が見つかりません")

        return {"status": "deleted", "id": registry_id}


# ====================
# 甲区（所有権）CRUD
# ====================
KOU_COLUMNS = [
    'id', 'registry_id', 'rank_number', 'purpose', 'reception_date', 'reception_number',
    'owner_name', 'owner_address', 'ownership_ratio', 'cause', 'cause_date', 'cause_detail',
    'is_active', 'deletion_date', 'deletion_reception_number', 'notes', 'created_at', 'updated_at'
]


@router.get("/registries/{registry_id}/kou", response_model=List[KouEntryResponse])
async def get_kou_entries(registry_id: int):
    """甲区エントリ一覧取得"""
    with READatabase.cursor() as (cur, conn):
        cur.execute(f"""
            SELECT {', '.join(KOU_COLUMNS)}
            FROM registry_kou_entries
            WHERE registry_id = %s AND deleted_at IS NULL
            ORDER BY rank_number
        """, (registry_id,))
        rows = cur.fetchall()

        items = []
        for row in rows:
            data = row_to_dict(row, KOU_COLUMNS)
            for key in ['reception_date', 'cause_date', 'deletion_date']:
                if data.get(key):
                    data[key] = str(data[key])
            items.append(KouEntryResponse(**data))

        return items


@router.post("/registries/{registry_id}/kou", response_model=KouEntryResponse)
async def create_kou_entry(registry_id: int, data: KouEntryCreate):
    """甲区エントリ追加"""
    with READatabase.cursor(commit=True) as (cur, conn):
        # 表題部存在確認
        cur.execute("SELECT id FROM property_registries WHERE id = %s AND deleted_at IS NULL", (registry_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="表題部が見つかりません")

        insert_data = data.model_dump(exclude_none=True)
        insert_data['registry_id'] = registry_id

        columns = list(insert_data.keys())
        values = [insert_data[col] for col in columns]
        placeholders = ', '.join(['%s'] * len(columns))

        cur.execute(f"""
            INSERT INTO registry_kou_entries ({', '.join(columns)})
            VALUES ({placeholders})
            RETURNING {', '.join(KOU_COLUMNS)}
        """, values)

        row = cur.fetchone()
        result = row_to_dict(row, KOU_COLUMNS)
        for key in ['reception_date', 'cause_date', 'deletion_date']:
            if result.get(key):
                result[key] = str(result[key])

        return KouEntryResponse(**result)


@router.put("/registries/kou/{entry_id}", response_model=KouEntryResponse)
async def update_kou_entry(entry_id: int, data: KouEntryCreate):
    """甲区エントリ更新"""
    with READatabase.cursor(commit=True) as (cur, conn):
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="更新データがありません")

        set_clauses = [f"{col} = %s" for col in update_data.keys()]
        values = list(update_data.values())
        values.append(entry_id)

        cur.execute(f"""
            UPDATE registry_kou_entries
            SET {', '.join(set_clauses)}, updated_at = NOW()
            WHERE id = %s AND deleted_at IS NULL
            RETURNING {', '.join(KOU_COLUMNS)}
        """, values)

        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="甲区エントリが見つかりません")

        result = row_to_dict(row, KOU_COLUMNS)
        for key in ['reception_date', 'cause_date', 'deletion_date']:
            if result.get(key):
                result[key] = str(result[key])

        return KouEntryResponse(**result)


@router.delete("/registries/kou/{entry_id}")
async def delete_kou_entry(entry_id: int):
    """甲区エントリ論理削除"""
    with READatabase.cursor(commit=True) as (cur, conn):
        cur.execute("UPDATE registry_kou_entries SET deleted_at = NOW() WHERE id = %s AND deleted_at IS NULL RETURNING id", (entry_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="甲区エントリが見つかりません")
        return {"status": "deleted", "id": entry_id}


# ====================
# 乙区（抵当権等）CRUD
# ====================
OTSU_COLUMNS = [
    'id', 'registry_id', 'rank_number', 'purpose', 'reception_date', 'reception_number',
    'debt_amount', 'interest_rate', 'damage_rate', 'debtor_name', 'debtor_address',
    'mortgagee_name', 'mortgagee_address', 'maximum_amount', 'debt_scope',
    'right_holder_name', 'right_holder_address', 'right_purpose', 'right_scope',
    'right_duration', 'rent_amount', 'cause', 'cause_date', 'joint_collateral_number',
    'is_active', 'deletion_date', 'deletion_reception_number', 'notes', 'created_at', 'updated_at'
]


@router.get("/registries/{registry_id}/otsu", response_model=List[OtsuEntryResponse])
async def get_otsu_entries(registry_id: int):
    """乙区エントリ一覧取得"""
    with READatabase.cursor() as (cur, conn):
        cur.execute(f"""
            SELECT {', '.join(OTSU_COLUMNS)}
            FROM registry_otsu_entries
            WHERE registry_id = %s AND deleted_at IS NULL
            ORDER BY rank_number
        """, (registry_id,))
        rows = cur.fetchall()

        items = []
        for row in rows:
            data = row_to_dict(row, OTSU_COLUMNS)
            for key in ['reception_date', 'cause_date', 'deletion_date']:
                if data.get(key):
                    data[key] = str(data[key])
            items.append(OtsuEntryResponse(**data))

        return items


@router.post("/registries/{registry_id}/otsu", response_model=OtsuEntryResponse)
async def create_otsu_entry(registry_id: int, data: OtsuEntryCreate):
    """乙区エントリ追加"""
    with READatabase.cursor(commit=True) as (cur, conn):
        # 表題部存在確認
        cur.execute("SELECT id FROM property_registries WHERE id = %s AND deleted_at IS NULL", (registry_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="表題部が見つかりません")

        insert_data = data.model_dump(exclude_none=True)
        insert_data['registry_id'] = registry_id

        columns = list(insert_data.keys())
        values = [insert_data[col] for col in columns]
        placeholders = ', '.join(['%s'] * len(columns))

        cur.execute(f"""
            INSERT INTO registry_otsu_entries ({', '.join(columns)})
            VALUES ({placeholders})
            RETURNING {', '.join(OTSU_COLUMNS)}
        """, values)

        row = cur.fetchone()
        result = row_to_dict(row, OTSU_COLUMNS)
        for key in ['reception_date', 'cause_date', 'deletion_date']:
            if result.get(key):
                result[key] = str(result[key])

        return OtsuEntryResponse(**result)


@router.put("/registries/otsu/{entry_id}", response_model=OtsuEntryResponse)
async def update_otsu_entry(entry_id: int, data: OtsuEntryCreate):
    """乙区エントリ更新"""
    with READatabase.cursor(commit=True) as (cur, conn):
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="更新データがありません")

        set_clauses = [f"{col} = %s" for col in update_data.keys()]
        values = list(update_data.values())
        values.append(entry_id)

        cur.execute(f"""
            UPDATE registry_otsu_entries
            SET {', '.join(set_clauses)}, updated_at = NOW()
            WHERE id = %s AND deleted_at IS NULL
            RETURNING {', '.join(OTSU_COLUMNS)}
        """, values)

        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="乙区エントリが見つかりません")

        result = row_to_dict(row, OTSU_COLUMNS)
        for key in ['reception_date', 'cause_date', 'deletion_date']:
            if result.get(key):
                result[key] = str(result[key])

        return OtsuEntryResponse(**result)


@router.delete("/registries/otsu/{entry_id}")
async def delete_otsu_entry(entry_id: int):
    """乙区エントリ論理削除"""
    with READatabase.cursor(commit=True) as (cur, conn):
        cur.execute("UPDATE registry_otsu_entries SET deleted_at = NOW() WHERE id = %s AND deleted_at IS NULL RETURNING id", (entry_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="乙区エントリが見つかりません")
        return {"status": "deleted", "id": entry_id}


# ====================
# 全情報取得（表題部 + 甲区 + 乙区）
# ====================
@router.get("/registries/{registry_id}/full")
async def get_registry_full(registry_id: int):
    """登記情報の全情報取得（表題部 + 甲区 + 乙区）"""
    with READatabase.cursor() as (cur, conn):
        # 表題部
        cur.execute(f"""
            SELECT {', '.join(REGISTRY_COLUMNS)}
            FROM property_registries
            WHERE id = %s AND deleted_at IS NULL
        """, (registry_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="登記情報が見つかりません")

        registry = row_to_dict(row, REGISTRY_COLUMNS)
        for key in ['built_date', 'ownership_date', 'mortgage_date', 'certified_date', 'title_cause_date']:
            if registry.get(key):
                registry[key] = str(registry[key])

        # 甲区
        cur.execute(f"""
            SELECT {', '.join(KOU_COLUMNS)}
            FROM registry_kou_entries
            WHERE registry_id = %s AND deleted_at IS NULL
            ORDER BY rank_number
        """, (registry_id,))
        kou_rows = cur.fetchall()
        kou_entries = []
        for r in kou_rows:
            data = row_to_dict(r, KOU_COLUMNS)
            for key in ['reception_date', 'cause_date', 'deletion_date']:
                if data.get(key):
                    data[key] = str(data[key])
            kou_entries.append(data)

        # 乙区
        cur.execute(f"""
            SELECT {', '.join(OTSU_COLUMNS)}
            FROM registry_otsu_entries
            WHERE registry_id = %s AND deleted_at IS NULL
            ORDER BY rank_number
        """, (registry_id,))
        otsu_rows = cur.fetchall()
        otsu_entries = []
        for r in otsu_rows:
            data = row_to_dict(r, OTSU_COLUMNS)
            for key in ['reception_date', 'cause_date', 'deletion_date']:
                if data.get(key):
                    data[key] = str(data[key])
            otsu_entries.append(data)

        return {
            "registry": registry,
            "kou_entries": kou_entries,
            "otsu_entries": otsu_entries
        }
