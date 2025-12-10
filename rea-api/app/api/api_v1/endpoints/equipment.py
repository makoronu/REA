from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from shared.database import READatabase

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_equipment():
    """全設備マスターをカテゴリ別に取得"""
    db = READatabase()
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, item_name, display_name, tab_group, data_type, display_order
            FROM equipment_master
            ORDER BY tab_group, COALESCE(display_order, 999), display_name
        """)

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@router.get("/grouped", response_model=Dict[str, List[Dict[str, Any]]])
async def get_equipment_grouped():
    """設備マスターをカテゴリごとにグループ化して取得"""
    db = READatabase()
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, item_name, display_name, tab_group, display_order
            FROM equipment_master
            ORDER BY tab_group, COALESCE(display_order, 999), display_name
        """)

        rows = cur.fetchall()

        grouped = {}
        for row in rows:
            item_id, item_name, display_name, tab_group, display_order = row
            if tab_group not in grouped:
                grouped[tab_group] = []
            grouped[tab_group].append({
                'id': item_id,
                'item_name': item_name,
                'display_name': display_name,
                'display_order': display_order or 999
            })

        return grouped

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@router.get("/categories", response_model=List[str])
async def get_equipment_categories():
    """設備カテゴリ一覧を取得"""
    db = READatabase()
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT DISTINCT tab_group
            FROM equipment_master
            WHERE tab_group IS NOT NULL
            ORDER BY tab_group
        """)

        return [row[0] for row in cur.fetchall()]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
