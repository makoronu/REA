"""
チラシ・マイソク生成APIエンドポイント
"""

import importlib.util
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

# REAルートをパスに追加
REA_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(REA_ROOT))

# rea-flyerモジュールを動的にロード（ハイフン対応）
FLYER_PATH = REA_ROOT / "rea-flyer"
sys.path.insert(0, str(FLYER_PATH))

from generators import MaisokuGenerator
from shared.database import READatabase

router = APIRouter()


def get_property_full_data(property_id: int) -> dict:
    """
    物件の全データを取得（properties + land_info + building_info結合）

    Args:
        property_id: 物件ID

    Returns:
        dict: 物件データ
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # propertiesテーブル
        cur.execute(
            """
            SELECT *
            FROM properties
            WHERE id = %s
            """,
            (property_id,),
        )
        columns = [desc[0] for desc in cur.description]
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="物件が見つかりません")

        property_data = dict(zip(columns, row))

        # land_infoテーブル
        cur.execute(
            """
            SELECT *
            FROM land_info
            WHERE property_id = %s
            """,
            (property_id,),
        )
        land_row = cur.fetchone()
        if land_row:
            land_columns = [desc[0] for desc in cur.description]
            land_data = dict(zip(land_columns, land_row))
            # id, property_id以外をマージ
            for key, value in land_data.items():
                if key not in ["id", "property_id", "created_at", "updated_at"]:
                    if value is not None or key not in property_data:
                        property_data[key] = value

        # building_infoテーブル
        cur.execute(
            """
            SELECT *
            FROM building_info
            WHERE property_id = %s
            """,
            (property_id,),
        )
        building_row = cur.fetchone()
        if building_row:
            building_columns = [desc[0] for desc in cur.description]
            building_data = dict(zip(building_columns, building_row))
            for key, value in building_data.items():
                if key not in ["id", "property_id", "created_at", "updated_at"]:
                    if value is not None or key not in property_data:
                        property_data[key] = value

        return property_data

    finally:
        cur.close()
        conn.close()


@router.post("/maisoku/{property_id}")
async def generate_maisoku(
    property_id: int,
    format: str = Query(default="svg", description="出力形式（svg/png）"),
):
    """
    マイソクを生成

    Args:
        property_id: 物件ID
        format: 出力形式（svg/png）

    Returns:
        SVGまたはPNG
    """
    try:
        # 物件データ取得
        property_data = get_property_full_data(property_id)

        # マイソク生成
        generator = MaisokuGenerator()
        svg_content = generator.generate(property_data)

        if format == "svg":
            return Response(
                content=svg_content,
                media_type="image/svg+xml",
                headers={
                    "Content-Disposition": f"attachment; filename=maisoku_{property_id}.svg"
                },
            )
        elif format == "png":
            # PNG変換（cairosvg使用）
            import cairosvg

            png_content = cairosvg.svg2png(bytestring=svg_content.encode("utf-8"))
            return Response(
                content=png_content,
                media_type="image/png",
                headers={
                    "Content-Disposition": f"attachment; filename=maisoku_{property_id}.png"
                },
            )
        else:
            raise HTTPException(status_code=400, detail=f"未対応の形式: {format}")

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"マイソク生成エラー: {str(e)}")


@router.get("/maisoku/{property_id}/preview")
async def preview_maisoku(property_id: int):
    """
    マイソクプレビュー（PNG形式）

    Args:
        property_id: 物件ID

    Returns:
        PNG画像
    """
    return await generate_maisoku(property_id, format="png")


@router.get("/templates")
async def list_templates():
    """
    利用可能なテンプレート一覧を取得

    Returns:
        dict: テンプレート一覧
    """
    try:
        generator = MaisokuGenerator()
        maisoku_templates = list(generator.maisoku_config.keys())
        chirashi_templates = list(
            generator.templates_config.get("chirashi", {}).keys()
        )

        return {
            "maisoku": maisoku_templates,
            "chirashi": chirashi_templates,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
