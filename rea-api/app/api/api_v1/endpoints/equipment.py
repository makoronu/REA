"""
設備マスターAPI

リファクタリング: 2025-12-15
- 3つのクエリを1つに統合
- コンテキストマネージャー使用
- カスタム例外使用
"""
from typing import Any, Dict, List

from fastapi import APIRouter

from app.core.exceptions import DatabaseError
from shared.database import READatabase
from shared.constants import DEFAULT_DISPLAY_ORDER_FALLBACK

router = APIRouter()


def _fetch_all_equipment() -> List[Dict[str, Any]]:
    """設備マスターを全件取得（内部関数）

    1回のクエリで全データを取得し、各エンドポイントで再利用
    """
    with READatabase.cursor() as (cur, conn):
        cur.execute("""
            SELECT id, item_name, display_name, tab_group, data_type, display_order
            FROM equipment_master
            ORDER BY tab_group, COALESCE(display_order, %s), display_name
        """, (DEFAULT_DISPLAY_ORDER_FALLBACK,))

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in rows]


@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_equipment():
    """全設備マスターを取得"""
    try:
        return _fetch_all_equipment()
    except Exception as e:
        raise DatabaseError(str(e))


@router.get("/grouped", response_model=Dict[str, List[Dict[str, Any]]])
async def get_equipment_grouped():
    """設備マスターをカテゴリごとにグループ化して取得"""
    try:
        all_equipment = _fetch_all_equipment()

        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for item in all_equipment:
            tab_group = item.get('tab_group')
            if tab_group not in grouped:
                grouped[tab_group] = []
            grouped[tab_group].append({
                'id': item['id'],
                'item_name': item['item_name'],
                'display_name': item['display_name'],
                'display_order': item.get('display_order') or DEFAULT_DISPLAY_ORDER_FALLBACK
            })

        return grouped
    except Exception as e:
        raise DatabaseError(str(e))


@router.get("/categories", response_model=List[str])
async def get_equipment_categories():
    """設備カテゴリ一覧を取得"""
    try:
        all_equipment = _fetch_all_equipment()

        # ユニークなカテゴリを抽出（順序保持）
        seen = set()
        categories = []
        for item in all_equipment:
            tab_group = item.get('tab_group')
            if tab_group and tab_group not in seen:
                seen.add(tab_group)
                categories.append(tab_group)

        return categories
    except Exception as e:
        raise DatabaseError(str(e))
