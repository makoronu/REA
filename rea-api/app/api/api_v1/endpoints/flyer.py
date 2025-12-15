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

from generators import MaisokuGenerator, ChirashiGenerator
from utils import ImageHandler
from shared.database import READatabase
from pydantic import BaseModel
from typing import List, Dict, Any


# フィールド名とmaster_category_codeのマッピング
MASTER_OPTION_FIELDS = {
    "use_district": "zoning_district",
    "land_category": "land_category",
    "land_rights": "land_rights",
    "city_planning": "city_planning",
    "setback": "setback",
    "transaction_type": "transaction_type",
    "delivery_timing": "delivery_timing",
    "building_structure": "building_structure",
}


def load_master_options_cache(conn) -> Dict[str, Dict[str, str]]:
    """
    master_optionsをキャッシュとして読み込む

    Returns:
        dict: {category_code: {option_code: option_value}}
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT mc.category_code, mo.option_code, mo.option_value
        FROM master_options mo
        JOIN master_categories mc ON mo.category_id = mc.id
        WHERE mc.category_code IN %s
    """, (tuple(MASTER_OPTION_FIELDS.values()),))

    cache = {}
    for row in cur.fetchall():
        category_code, option_code, option_value = row
        if category_code not in cache:
            cache[category_code] = {}
        cache[category_code][str(option_code)] = option_value
    cur.close()
    return cache


def convert_master_options_to_labels(
    property_data: Dict[str, Any],
    cache: Dict[str, Dict[str, str]]
) -> Dict[str, Any]:
    """
    物件データ内のmaster_option値をラベルに変換

    Args:
        property_data: 物件データ
        cache: master_optionsキャッシュ

    Returns:
        dict: ラベル変換済み物件データ
    """
    for field_name, category_code in MASTER_OPTION_FIELDS.items():
        if field_name in property_data:
            value = property_data[field_name]
            if value is not None and category_code in cache:
                str_value = str(value)
                if str_value in cache[category_code]:
                    property_data[field_name] = cache[category_code][str_value]
                elif str_value == "0":
                    # 0は「未設定」として空文字に
                    property_data[field_name] = ""
    return property_data


class ChirashiRequest(BaseModel):
    """チラシ生成リクエスト"""
    property_ids: List[int]
    layout: str = "single"  # single, dual, grid

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

        # 画像データ取得（メタデータ駆動）
        image_handler = ImageHandler()

        # 複数画像対応（マイソク用に5枚まで取得）
        images_data = image_handler.get_images_for_svg(property_id, conn, max_images=5)
        property_data["_images"] = images_data

        # 後方互換性のため_main_imageも維持
        if "main_image" in images_data:
            property_data["_main_image"] = images_data["main_image"]
        else:
            property_data["_main_image"] = image_handler.get_image_for_svg(property_id, conn)

        # master_option値をラベルに変換
        master_cache = load_master_options_cache(conn)
        property_data = convert_master_options_to_labels(property_data, master_cache)

        return property_data

    finally:
        cur.close()
        conn.close()


@router.post("/maisoku/{property_id}")
async def generate_maisoku(
    property_id: int,
    format: str = Query(default="svg", description="出力形式（svg/png/pdf）"),
):
    """
    マイソクを生成

    Args:
        property_id: 物件ID
        format: 出力形式（svg/png/pdf）
            - svg: 編集可能、Illustrator対応
            - png: Web表示用
            - pdf: 印刷入稿用（CMYK、塗り足し3mm込み）

    Returns:
        SVG/PNG/PDF
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
        elif format == "pdf":
            # PDF変換（印刷入稿用）
            import cairosvg

            pdf_content = cairosvg.svg2pdf(bytestring=svg_content.encode("utf-8"))
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=maisoku_{property_id}.pdf"
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


@router.post("/chirashi")
async def generate_chirashi(
    request: ChirashiRequest,
    format: str = Query(default="svg", description="出力形式（svg/png/pdf）"),
):
    """
    チラシを生成（複数物件対応）

    Args:
        request: チラシ生成リクエスト（property_ids, layout）
        format: 出力形式（svg/png）

    Returns:
        SVGまたはPNG
    """
    try:
        # 物件データ取得
        properties = []
        for pid in request.property_ids:
            try:
                prop_data = get_property_full_data(pid)
                properties.append(prop_data)
            except HTTPException:
                continue  # 存在しない物件はスキップ

        if not properties:
            raise HTTPException(status_code=404, detail="有効な物件が見つかりません")

        # チラシ生成
        generator = ChirashiGenerator()
        svg_content = generator.generate_multi(properties, layout=request.layout)

        ids_str = "_".join(str(pid) for pid in request.property_ids[:4])

        if format == "svg":
            return Response(
                content=svg_content,
                media_type="image/svg+xml",
                headers={
                    "Content-Disposition": f"attachment; filename=chirashi_{ids_str}.svg"
                },
            )
        elif format == "png":
            import cairosvg

            png_content = cairosvg.svg2png(bytestring=svg_content.encode("utf-8"))
            return Response(
                content=png_content,
                media_type="image/png",
                headers={
                    "Content-Disposition": f"attachment; filename=chirashi_{ids_str}.png"
                },
            )
        elif format == "pdf":
            import cairosvg

            pdf_content = cairosvg.svg2pdf(bytestring=svg_content.encode("utf-8"))
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=chirashi_{ids_str}.pdf"
                },
            )
        else:
            raise HTTPException(status_code=400, detail=f"未対応の形式: {format}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"チラシ生成エラー: {str(e)}")


@router.get("/chirashi/{property_id}/preview")
async def preview_chirashi(property_id: int):
    """
    チラシプレビュー（単一物件、PNG形式）

    Args:
        property_id: 物件ID

    Returns:
        PNG画像
    """
    request = ChirashiRequest(property_ids=[property_id], layout="single")
    return await generate_chirashi(request, format="png")


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
