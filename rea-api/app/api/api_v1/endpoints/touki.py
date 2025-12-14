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
    """改良版パース（登記情報提供サービスPDF対応）"""
    import re

    # 全角→半角変換
    zenkaku_to_hankaku = str.maketrans('０１２３４５６７８９：．，', '0123456789:.,')
    def normalize(text):
        return text.translate(zenkaku_to_hankaku)

    result = {
        'document_type': 'unknown',
        'real_estate_number': None,
        'land_info': {},
        'building_info': {},
        'owner_info': {},
        'mortgage_info': [],
        'parsed_at': datetime.now().isoformat()
    }

    # 土地/建物判定
    has_land = '土地の表示' in raw_text
    has_building = '建物の表示' in raw_text or '主である建物の表示' in raw_text
    if has_land and has_building:
        result['document_type'] = 'both'
    elif has_building:
        result['document_type'] = 'building'
    elif has_land:
        result['document_type'] = 'land'

    # 不動産番号
    match = re.search(r'不動産番号[│\|]?\s*([０-９\d]+)', raw_text)
    if match:
        result['real_estate_number'] = normalize(match.group(1))

    # 土地情報
    if result['document_type'] in ['land', 'both']:
        # 所在
        matches = re.findall(r'所\s*在[│\|]([^│┃\n]+)', raw_text)
        for loc in reversed(matches):
            loc = loc.strip()
            if loc and not re.search(r'年|月|日|変更|登記', loc):
                result['land_info']['location'] = loc
                break

        # 地番
        match = re.search(r'([０-９\d]+番[０-９\d]*)\s*│', raw_text)
        if match:
            result['land_info']['lot_number'] = normalize(match.group(1))

        # 地目
        for cat in ['宅地', '畑', '田', '山林', '原野', '雑種地']:
            if f'│{cat}' in raw_text or f'│ {cat}' in raw_text:
                result['land_info']['land_category'] = cat

        # 地積
        area_matches = re.findall(r'│\s*([０-９\d]+)[：:]([０-９\d]+)\s*│', raw_text)
        if area_matches:
            whole, decimal = area_matches[-1]
            area = float(normalize(whole)) + float(normalize(decimal)) / 100
            result['land_info']['land_area_m2'] = round(area, 2)

    # 建物情報
    if result['document_type'] in ['building', 'both']:
        # 所在
        matches = re.findall(r'所\s*在[│\|]([^│┃\n]+)', raw_text)
        for loc in reversed(matches):
            loc = loc.strip()
            if loc and not re.search(r'年|月|日|変更|登記', loc):
                result['building_info']['location'] = loc
                break

        # 家屋番号
        match = re.search(r'家屋番号[│\|]\s*([^│┃\n]+)', raw_text)
        if match:
            result['building_info']['building_number'] = normalize(match.group(1).strip())

        # 種類
        if '居宅' in raw_text:
            result['building_info']['building_type'] = '居宅'

        # 構造
        match = re.search(r'│(木造[^│\n]+階)', raw_text)
        if match:
            result['building_info']['structure'] = match.group(1) + '建'

        # 床面積
        floor_matches = re.findall(r'([１２３４５６７８９\d]+)階\s*([０-９\d]+)[：:]([０-９\d]+)', raw_text)
        if floor_matches:
            floor_areas = {}
            total = 0.0
            for floor, whole, decimal in floor_matches:
                floor_num = int(normalize(floor))
                area = float(normalize(whole)) + float(normalize(decimal)) / 100
                floor_areas[f'floor_{floor_num}'] = round(area, 2)
                total += area
            result['building_info']['floor_areas'] = floor_areas
            result['building_info']['total_floor_area_m2'] = round(total, 2)

        # 新築日
        match = re.search(r'(昭和|平成|令和)([０-９\d]+)年([０-９\d]+)月([０-９\d]+)日新築', raw_text)
        if match:
            era, y, m, d = match.groups()
            era_start = {'昭和': 1926, '平成': 1989, '令和': 2019}
            year = era_start.get(era, 1926) + int(normalize(y)) - 1
            result['building_info']['construction_date'] = f"{year}-{int(normalize(m)):02d}-{int(normalize(d)):02d}"

    # 所有者（行ごとに処理して最新を取得）
    owner_blocks = []
    lines = raw_text.split('\n')
    for i, line in enumerate(lines):
        if '所有者' in line and '登記名義人' not in line:
            addr_match = re.search(r'所有者\s+([^┃\n]+)', line)
            if addr_match:
                address = addr_match.group(1).strip().rstrip('│')
                # 次の数行から名前を探す（住所が複数行にまたがる場合対応）
                for offset in range(1, 4):
                    if i + offset >= len(lines):
                        break
                    check_line = lines[i + offset]
                    # 名前パターン: ┃で終わる行の中身、または│...┃の間
                    name_match = re.search(r'[│┃]\s*([^│┃\d０-９\n]{2,})\s*┃', check_line)
                    if not name_match:
                        # 行末が┃で、漢字名前がある場合
                        name_match = re.search(r'^\s*([^\d０-９│┃\n]{2,})\s*┃$', check_line)
                    if name_match:
                        name = re.sub(r'\s+', '', name_match.group(1).strip())
                        # 名前らしいか判定（2文字以上の非数字で、登記関連用語でない）
                        skip_words = ['移記', '登記', '原因', '売買', '相続', '平成', '昭和', '令和', '順位']
                        if name and len(name) >= 2 and not any(w in name for w in skip_words):
                            owner_blocks.append({
                                'address': address,
                                'name': name
                            })
                            break

    if owner_blocks:
        latest = owner_blocks[-1]
        result['owner_info']['owner_address'] = latest['address']
        result['owner_info']['owner_name'] = latest['name']

    # 抵当権
    if '抵当権設定' in raw_text:
        amount_matches = re.findall(r'債権額\s*金([０-９\d,，]+)万?円', raw_text)
        for amount_str in amount_matches:
            amount = int(normalize(amount_str).replace(',', ''))
            result['mortgage_info'].append({'type': '抵当権', 'amount': amount})

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
