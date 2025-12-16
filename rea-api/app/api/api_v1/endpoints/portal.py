"""
ポータルサイト連携API

HOMES/SUUMO/athome等へのCSV出力
"""

import sys
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

# パス設定
_pkg_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from shared.database import READatabase
from app.services.portal.homes_exporter import HomesExporter


router = APIRouter()


class ExportRequest(BaseModel):
    """CSV出力リクエスト"""
    property_ids: List[int]
    test_mode: bool = False


class ValidationResult(BaseModel):
    """バリデーション結果"""
    valid: bool
    errors: dict


@router.post("/homes/export")
async def export_homes_csv(request: ExportRequest):
    """HOMES CSV出力

    Args:
        request: 出力対象の物件IDリスト

    Returns:
        Shift_JIS エンコードされたCSVファイル
    """
    if not request.property_ids:
        raise HTTPException(status_code=400, detail="property_ids is required")

    try:
        db = READatabase()
        conn = db.get_connection()

        exporter = HomesExporter(conn)
        csv_bytes = exporter.export_properties(request.property_ids)

        conn.close()

        # ファイル名
        from datetime import datetime
        filename = f"homes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return Response(
            content=csv_bytes,
            media_type="text/csv; charset=shift_jis",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/homes/validate", response_model=ValidationResult)
async def validate_homes_export(request: ExportRequest):
    """HOMES出力前バリデーション

    Args:
        request: チェック対象の物件IDリスト

    Returns:
        バリデーション結果
    """
    if not request.property_ids:
        raise HTTPException(status_code=400, detail="property_ids is required")

    try:
        db = READatabase()
        conn = db.get_connection()

        exporter = HomesExporter(conn)
        errors = exporter.validate_properties(request.property_ids)

        conn.close()

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/homes/field-mapping")
async def get_homes_field_mapping():
    """HOMESフィールドマッピング定義を取得

    Returns:
        マッピング定義（YAMLをJSONに変換）
    """
    import yaml
    from pathlib import Path

    mapping_path = Path(__file__).parent.parent.parent.parent.parent.parent / 'docs' / 'portal' / 'homes_field_mapping.yaml'

    if not mapping_path.exists():
        raise HTTPException(status_code=404, detail="マッピングファイルが見つかりません")

    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = yaml.safe_load(f)

    return mapping
