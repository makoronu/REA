"""
登記事項証明書インポートAPI
"""
import os
import sys
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from pydantic import BaseModel

# パーサーのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'rea-scraper'))

from shared.database import READatabase

# pdfplumber
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

router = APIRouter()

# アップロード先ディレクトリ
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'uploads', 'touki')
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ToukiImportResponse(BaseModel):
    id: int
    file_name: str
    status: str
    raw_text: Optional[str] = None
    parsed_data: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime


class ToukiListResponse(BaseModel):
    items: List[ToukiImportResponse]
    total: int


@router.post("/upload", response_model=ToukiImportResponse)
async def upload_touki_pdf(file: UploadFile = File(...)):
    """
    登記事項証明書PDFをアップロードしてテキスト抽出
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="PDFファイルのみ対応しています")

    if pdfplumber is None:
        raise HTTPException(status_code=500, detail="pdfplumber not installed")

    # ファイル保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    content = await file.read()
    with open(file_path, 'wb') as f:
        f.write(content)

    # テキスト抽出
    raw_text = None
    error_message = None

    try:
        all_text = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    all_text.append(f"--- Page {i + 1} ---\n{text}")
        raw_text = "\n\n".join(all_text)
    except Exception as e:
        error_message = str(e)

    # DB保存
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO touki_imports (file_name, file_path, raw_text, status, error_message)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (
            file.filename,
            file_path,
            raw_text,
            'uploaded' if raw_text else 'error',
            error_message
        ))

        row = cur.fetchone()
        conn.commit()

        return ToukiImportResponse(
            id=row[0],
            file_name=file.filename,
            status='uploaded' if raw_text else 'error',
            raw_text=raw_text,
            error_message=error_message,
            created_at=row[1]
        )

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.get("/list", response_model=ToukiListResponse)
async def list_touki_imports(
    status: Optional[str] = Query(None, description="フィルタ: uploaded/parsed/imported/error"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    インポート一覧を取得
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # カウント
        count_sql = "SELECT COUNT(*) FROM touki_imports"
        if status:
            count_sql += " WHERE status = %s"
            cur.execute(count_sql, (status,))
        else:
            cur.execute(count_sql)
        total = cur.fetchone()[0]

        # データ取得
        sql = """
            SELECT id, file_name, status, raw_text, parsed_data, error_message, created_at
            FROM touki_imports
        """
        params = []
        if status:
            sql += " WHERE status = %s"
            params.append(status)
        sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(sql, params)
        rows = cur.fetchall()

        items = [
            ToukiImportResponse(
                id=row[0],
                file_name=row[1],
                status=row[2],
                raw_text=row[3][:500] if row[3] else None,  # 一覧では先頭500文字のみ
                parsed_data=row[4],
                error_message=row[5],
                created_at=row[6]
            )
            for row in rows
        ]

        return ToukiListResponse(items=items, total=total)

    finally:
        cur.close()
        conn.close()


@router.get("/{import_id}", response_model=ToukiImportResponse)
async def get_touki_import(import_id: int):
    """
    インポート詳細を取得
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id, file_name, status, raw_text, parsed_data, error_message, created_at
            FROM touki_imports
            WHERE id = %s
        """, (import_id,))

        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Not found")

        return ToukiImportResponse(
            id=row[0],
            file_name=row[1],
            status=row[2],
            raw_text=row[3],
            parsed_data=row[4],
            error_message=row[5],
            created_at=row[6]
        )

    finally:
        cur.close()
        conn.close()


@router.post("/{import_id}/parse")
async def parse_touki_import(import_id: int):
    """
    アップロード済みのテキストをパースして構造化
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # データ取得
        cur.execute("SELECT raw_text FROM touki_imports WHERE id = %s", (import_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Not found")

        raw_text = row[0]
        if not raw_text:
            raise HTTPException(status_code=400, detail="No text to parse")

        # パーサーをインポート
        try:
            from src.parsers.touki.touki_parser import ToukiParser
            parser = ToukiParser()
            parsed_data = parser.parse(raw_text)
        except ImportError:
            # フォールバック: シンプルなパース
            parsed_data = simple_parse(raw_text)

        # 更新
        cur.execute("""
            UPDATE touki_imports
            SET parsed_data = %s, status = 'parsed', updated_at = NOW()
            WHERE id = %s
        """, (
            __import__('json').dumps(parsed_data, ensure_ascii=False),
            import_id
        ))
        conn.commit()

        return {"status": "success", "parsed_data": parsed_data}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


def simple_parse(raw_text: str) -> dict:
    """シンプルなパース（フォールバック用）"""
    import re

    result = {
        'document_type': 'unknown',
        'land_info': {},
        'building_info': {},
        'parsed_at': datetime.now().isoformat()
    }

    # 土地/建物判定
    if '土地の表示' in raw_text or '地番' in raw_text:
        result['document_type'] = 'land'
    if '建物の表示' in raw_text or '家屋番号' in raw_text:
        result['document_type'] = 'building' if result['document_type'] == 'unknown' else 'both'

    # 基本的な抽出
    patterns = {
        'location': r'所在[　\s]+(.+?)(?:\n|$)',
        'lot_number': r'地番[　\s]+(.+?)(?:\n|$)',
        'land_category': r'地目[　\s]+(.+?)(?:\n|$)',
        'land_area': r'地積[　\s]+([\d,.]+)',
        'building_number': r'家屋番号[　\s]+(.+?)(?:\n|$)',
        'structure': r'構造[　\s]+(.+?)(?:\n|$)',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, raw_text)
        if match:
            if key in ['location', 'lot_number', 'land_category', 'land_area']:
                result['land_info'][key] = match.group(1).strip()
            else:
                result['building_info'][key] = match.group(1).strip()

    return result


@router.delete("/{import_id}")
async def delete_touki_import(import_id: int):
    """
    インポートを削除
    """
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # ファイルパス取得
        cur.execute("SELECT file_path FROM touki_imports WHERE id = %s", (import_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Not found")

        file_path = row[0]

        # DB削除
        cur.execute("DELETE FROM touki_imports WHERE id = %s", (import_id,))
        conn.commit()

        # ファイル削除
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        return {"status": "deleted"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
