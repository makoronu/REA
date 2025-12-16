"""
チラシ・マイソク生成 APIエンドポイント

POST /api/v1/flyer/maisoku/{property_id} - マイソクSVG生成
POST /api/v1/flyer/chirashi - チラシSVG生成（複数物件対応）
GET /api/v1/flyer/templates - 利用可能テンプレート一覧
GET /api/v1/flyer/preview/{property_id} - プレビュー画像生成
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

# rea-flyerモジュールをインポート
import sys
from pathlib import Path

# rea-flyerをパスに追加
rea_flyer_path = Path(__file__).parent.parent.parent.parent.parent.parent / 'rea-flyer'
sys.path.insert(0, str(rea_flyer_path))

from generators.maisoku import MaisokuGenerator
from generators.chirashi import ChirashiGenerator

logger = logging.getLogger(__name__)
router = APIRouter()


class ChirashiRequest(BaseModel):
    """チラシ生成リクエスト"""
    property_ids: List[int]
    layout: str = "single"  # single, dual, grid


@router.post("/maisoku/{property_id}")
async def generate_maisoku(
    property_id: int,
    template: Optional[str] = Query(None, description="テンプレート名（省略時は自動選択）")
):
    """
    マイソクSVGを生成

    Args:
        property_id: 物件ID
        template: テンプレート名（land, detached, apartment, investment）

    Returns:
        SVGファイル
    """
    try:
        # 物件データ取得
        from app.services.property_service import PropertyService
        service = PropertyService()
        property_data = await service.get_property_full(property_id)

        if not property_data:
            raise HTTPException(status_code=404, detail="物件が見つかりません")

        # マイソク生成
        generator = MaisokuGenerator()
        svg_content = generator.generate(property_data, template)

        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                "Content-Disposition": f'attachment; filename="maisoku_{property_id}.svg"'
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"設定ファイルエラー: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"マイソク生成エラー: {e}")
        raise HTTPException(status_code=500, detail="マイソク生成に失敗しました")


@router.post("/chirashi")
async def generate_chirashi(request: ChirashiRequest):
    """
    チラシSVGを生成（複数物件対応）

    Args:
        request: チラシ生成リクエスト

    Returns:
        SVGファイル
    """
    try:
        # 物件データ取得
        from app.services.property_service import PropertyService
        service = PropertyService()

        properties = []
        for pid in request.property_ids:
            property_data = await service.get_property_full(pid)
            if property_data:
                properties.append(property_data)

        if not properties:
            raise HTTPException(status_code=404, detail="物件が見つかりません")

        # チラシ生成
        generator = ChirashiGenerator()
        svg_content = generator.generate_multi(properties, request.layout)

        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                "Content-Disposition": f'attachment; filename="chirashi.svg"'
            }
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"設定ファイルエラー: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"チラシ生成エラー: {e}")
        raise HTTPException(status_code=500, detail="チラシ生成に失敗しました")


@router.get("/templates")
async def get_templates():
    """
    利用可能なテンプレート一覧を取得

    Returns:
        テンプレート一覧
    """
    try:
        generator = MaisokuGenerator()
        templates_config = generator.templates

        return {
            "maisoku": list(templates_config.get('maisoku', {}).keys()),
            "chirashi": list(templates_config.get('chirashi', {}).keys()),
        }

    except Exception as e:
        logger.error(f"テンプレート一覧取得エラー: {e}")
        raise HTTPException(status_code=500, detail="テンプレート一覧の取得に失敗しました")


@router.get("/preview/{property_id}")
async def generate_preview(
    property_id: int,
    type: str = Query("maisoku", description="maisoku or chirashi"),
    template: Optional[str] = Query(None, description="テンプレート名")
):
    """
    プレビュー画像を生成

    Args:
        property_id: 物件ID
        type: maisoku or chirashi
        template: テンプレート名

    Returns:
        PNG画像
    """
    try:
        # まずSVGを生成
        from app.services.property_service import PropertyService
        service = PropertyService()
        property_data = await service.get_property_full(property_id)

        if not property_data:
            raise HTTPException(status_code=404, detail="物件が見つかりません")

        if type == "maisoku":
            generator = MaisokuGenerator()
            svg_content = generator.generate(property_data, template)
        else:
            generator = ChirashiGenerator()
            svg_content = generator.generate(property_data, template)

        # SVG→PNG変換（cairosvgが必要）
        try:
            import cairosvg
            png_content = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))

            return Response(
                content=png_content,
                media_type="image/png",
                headers={
                    "Content-Disposition": f'inline; filename="preview_{property_id}.png"'
                }
            )
        except ImportError:
            # cairosvgがない場合はSVGを返す
            return Response(
                content=svg_content,
                media_type="image/svg+xml"
            )

    except Exception as e:
        logger.error(f"プレビュー生成エラー: {e}")
        raise HTTPException(status_code=500, detail="プレビュー生成に失敗しました")
