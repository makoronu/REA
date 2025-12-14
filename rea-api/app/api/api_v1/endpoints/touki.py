"""
登記事項証明書インポートAPI
"""
import os
import sys
import json
from datetime import datetime, date
from typing import List, Optional, Any
from decimal import Decimal

from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Body
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


# ========== Pydantic Models ==========

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


class ToukiRecordResponse(BaseModel):
    id: int
    real_estate_number: Optional[str] = None
    document_type: str
    location: str
    lot_number: Optional[str] = None
    land_category: Optional[str] = None
    land_area_m2: Optional[float] = None
    building_number: Optional[str] = None
    building_type: Optional[str] = None
    structure: Optional[str] = None
    floor_area_m2: Optional[float] = None
    floor_areas: Optional[dict] = None
    construction_date: Optional[date] = None
    owners: List[dict] = []
    mortgages: List[dict] = []
    touki_import_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ToukiRecordListResponse(BaseModel):
    items: List[ToukiRecordResponse]
    total: int


class CreatePropertyFromToukiRequest(BaseModel):
    land_touki_record_id: Optional[int] = None
    building_touki_record_id: Optional[int] = None


class LinkToukiRequest(BaseModel):
    property_id: int
    touki_record_id: int
    link_type: str = "main_land"


@router.post("/upload", response_model=ToukiImportResponse)
async def upload_touki_pdf(file: UploadFile = File(...)):
    """
    登記事項証明書PDFをアップロードしてテキスト抽出
    """
    if not file.filename.lower().endswith('.pdf'):
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
    アップロード済みのテキストをパースして構造化し、touki_recordsに保存
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

        # touki_importsを更新
        cur.execute("""
            UPDATE touki_imports
            SET parsed_data = %s, status = 'parsed', updated_at = NOW()
            WHERE id = %s
        """, (
            json.dumps(parsed_data, ensure_ascii=False),
            import_id
        ))

        # touki_recordsに保存
        touki_record_ids = save_to_touki_records(cur, import_id, parsed_data)

        conn.commit()

        return {
            "status": "success",
            "parsed_data": parsed_data,
            "touki_record_ids": touki_record_ids
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


def save_to_touki_records(cur, import_id: int, parsed_data: dict) -> List[int]:
    """パース結果をtouki_recordsに保存"""
    record_ids = []
    doc_type = parsed_data.get('document_type', 'unknown')

    # 所有者情報
    owner_info = parsed_data.get('owner_info', {})
    owners = []
    if owner_info.get('owner_name'):
        owners.append({
            'name': owner_info.get('owner_name'),
            'address': owner_info.get('owner_address')
        })

    # 抵当権情報
    mortgages = parsed_data.get('mortgage_info', [])

    # 土地レコード
    if doc_type in ['land', 'both']:
        land = parsed_data.get('land_info', {})
        location = land.get('location', '')
        if location:
            cur.execute("""
                INSERT INTO touki_records (
                    real_estate_number, document_type, location,
                    lot_number, land_category, land_area_m2,
                    owners, mortgages, touki_import_id, raw_parsed
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                parsed_data.get('real_estate_number'),
                'land',
                location,
                land.get('lot_number'),
                land.get('land_category'),
                land.get('land_area_m2'),
                json.dumps(owners, ensure_ascii=False),
                json.dumps(mortgages, ensure_ascii=False),
                import_id,
                json.dumps(parsed_data, ensure_ascii=False)
            ))
            record_ids.append(cur.fetchone()[0])

    # 建物レコード
    if doc_type in ['building', 'both']:
        building = parsed_data.get('building_info', {})
        location = building.get('location', '')
        if location:
            # 床面積
            floor_areas = building.get('floor_areas', {})
            # construction_date をdate型に変換
            construction_date = None
            if building.get('construction_date'):
                try:
                    construction_date = datetime.strptime(
                        building['construction_date'], '%Y-%m-%d'
                    ).date()
                except:
                    pass

            cur.execute("""
                INSERT INTO touki_records (
                    real_estate_number, document_type, location,
                    building_number, building_type, structure,
                    floor_area_m2, floor_areas, construction_date,
                    owners, mortgages, touki_import_id, raw_parsed
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                parsed_data.get('real_estate_number'),
                'building',
                location,
                building.get('building_number'),
                building.get('building_type'),
                building.get('structure'),
                building.get('total_floor_area_m2'),
                json.dumps(floor_areas, ensure_ascii=False) if floor_areas else None,
                construction_date,
                json.dumps(owners, ensure_ascii=False),
                json.dumps(mortgages, ensure_ascii=False),
                import_id,
                json.dumps(parsed_data, ensure_ascii=False)
            ))
            record_ids.append(cur.fetchone()[0])

    return record_ids


# ========== touki_records エンドポイント ==========

@router.get("/records/list", response_model=ToukiRecordListResponse)
async def list_touki_records(
    document_type: Optional[str] = Query(None, description="land/building/unit"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """登記レコード一覧"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # カウント
        count_sql = "SELECT COUNT(*) FROM touki_records"
        params = []
        if document_type:
            count_sql += " WHERE document_type = %s"
            params.append(document_type)
        cur.execute(count_sql, params)
        total = cur.fetchone()[0]

        # データ取得
        sql = """
            SELECT id, real_estate_number, document_type, location,
                   lot_number, land_category, land_area_m2,
                   building_number, building_type, structure,
                   floor_area_m2, floor_areas, construction_date,
                   owners, mortgages, touki_import_id, created_at
            FROM touki_records
        """
        params = []
        if document_type:
            sql += " WHERE document_type = %s"
            params.append(document_type)
        sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(sql, params)
        rows = cur.fetchall()

        items = []
        for row in rows:
            items.append(ToukiRecordResponse(
                id=row[0],
                real_estate_number=row[1],
                document_type=row[2],
                location=row[3],
                lot_number=row[4],
                land_category=row[5],
                land_area_m2=float(row[6]) if row[6] else None,
                building_number=row[7],
                building_type=row[8],
                structure=row[9],
                floor_area_m2=float(row[10]) if row[10] else None,
                floor_areas=row[11],
                construction_date=row[12],
                owners=row[13] if row[13] else [],
                mortgages=row[14] if row[14] else [],
                touki_import_id=row[15],
                created_at=row[16]
            ))

        return ToukiRecordListResponse(items=items, total=total)

    finally:
        cur.close()
        conn.close()


@router.get("/records/{record_id}", response_model=ToukiRecordResponse)
async def get_touki_record(record_id: int):
    """登記レコード詳細"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id, real_estate_number, document_type, location,
                   lot_number, land_category, land_area_m2,
                   building_number, building_type, structure,
                   floor_area_m2, floor_areas, construction_date,
                   owners, mortgages, touki_import_id, created_at
            FROM touki_records WHERE id = %s
        """, (record_id,))

        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Not found")

        return ToukiRecordResponse(
            id=row[0],
            real_estate_number=row[1],
            document_type=row[2],
            location=row[3],
            lot_number=row[4],
            land_category=row[5],
            land_area_m2=float(row[6]) if row[6] else None,
            building_number=row[7],
            building_type=row[8],
            structure=row[9],
            floor_area_m2=float(row[10]) if row[10] else None,
            floor_areas=row[11],
            construction_date=row[12],
            owners=row[13] if row[13] else [],
            mortgages=row[14] if row[14] else [],
            touki_import_id=row[15],
            created_at=row[16]
        )

    finally:
        cur.close()
        conn.close()


@router.post("/records/create-property")
async def create_property_from_touki(request: CreatePropertyFromToukiRequest):
    """登記レコードから物件を作成"""
    if not request.land_touki_record_id and not request.building_touki_record_id:
        raise HTTPException(status_code=400, detail="土地または建物の登記レコードIDが必要です")

    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        land_record = None
        building_record = None

        # 土地レコード取得
        if request.land_touki_record_id:
            cur.execute("SELECT * FROM touki_records WHERE id = %s", (request.land_touki_record_id,))
            land_record = cur.fetchone()
            if not land_record:
                raise HTTPException(status_code=404, detail="土地登記レコードが見つかりません")

        # 建物レコード取得
        if request.building_touki_record_id:
            cur.execute("SELECT * FROM touki_records WHERE id = %s", (request.building_touki_record_id,))
            building_record = cur.fetchone()
            if not building_record:
                raise HTTPException(status_code=404, detail="建物登記レコードが見つかりません")

        # 物件タイプ判定
        if land_record and building_record:
            property_type = '中古戸建'
        elif building_record:
            property_type = '中古戸建'
        else:
            property_type = '売地'

        # 所在地（建物優先、なければ土地）
        location = ''
        if building_record:
            location = building_record[3]  # location
        elif land_record:
            location = land_record[3]

        # 所有者情報
        owners = []
        if building_record and building_record[13]:  # owners
            owners = building_record[13]
        elif land_record and land_record[13]:
            owners = land_record[13]

        owner_name = owners[0]['name'] if owners else None
        owner_address = owners[0]['address'] if owners else None

        # propertiesに挿入（owner_name, owner_addressはpropertiesテーブルにないので、remarksに保存）
        owner_remarks = ""
        if owner_name:
            owner_remarks = f"所有者: {owner_name}"
            if owner_address:
                owner_remarks += f" ({owner_address})"

        cur.execute("""
            INSERT INTO properties (
                property_name, property_type, address, remarks,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (
            location,  # property_name = 所在地
            property_type,
            location,
            owner_remarks
        ))
        property_id = cur.fetchone()[0]

        # land_infoに挿入
        if land_record:
            cur.execute("""
                INSERT INTO land_info (
                    property_id, chiban, land_category, land_area, address
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                property_id,
                land_record[4],   # lot_number -> chiban
                land_record[5],   # land_category
                land_record[6],   # land_area_m2 -> land_area
                land_record[3]    # location -> address
            ))

        # building_infoに挿入
        if building_record:
            # 構造から階数を抽出（例: "木造亜鉛メッキ鋼板葺2階建" -> 2）
            floors_above = None
            structure = building_record[9]
            if structure:
                import re
                floor_match = re.search(r'(\d+)階', structure)
                if floor_match:
                    floors_above = int(floor_match.group(1))

            cur.execute("""
                INSERT INTO building_info (
                    property_id, building_structure, total_floor_area,
                    construction_date, building_floors_above
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                property_id,
                structure,                # structure -> building_structure
                building_record[10],      # floor_area_m2 -> total_floor_area
                building_record[12],      # construction_date
                floors_above
            ))

        # property_touki_linksに挿入
        if land_record:
            cur.execute("""
                INSERT INTO property_touki_links (property_id, touki_record_id, link_type)
                VALUES (%s, %s, 'main_land')
            """, (property_id, request.land_touki_record_id))

        if building_record:
            cur.execute("""
                INSERT INTO property_touki_links (property_id, touki_record_id, link_type)
                VALUES (%s, %s, 'main_building')
            """, (property_id, request.building_touki_record_id))

        conn.commit()

        return {
            "status": "success",
            "property_id": property_id,
            "message": f"物件ID {property_id} を作成しました"
        }

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.post("/records/link")
async def link_touki_to_property(request: LinkToukiRequest):
    """既存物件に登記レコードを紐付け"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        # 物件存在確認
        cur.execute("SELECT id FROM properties WHERE id = %s", (request.property_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="物件が見つかりません")

        # 登記レコード存在確認
        cur.execute("SELECT id FROM touki_records WHERE id = %s", (request.touki_record_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="登記レコードが見つかりません")

        # 紐付け
        cur.execute("""
            INSERT INTO property_touki_links (property_id, touki_record_id, link_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (property_id, touki_record_id) DO UPDATE SET link_type = %s
        """, (request.property_id, request.touki_record_id, request.link_type, request.link_type))

        conn.commit()

        return {"status": "success", "message": "紐付けました"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.delete("/records/{record_id}")
async def delete_touki_record(record_id: int):
    """登記レコードを削除"""
    db = READatabase()
    conn = db.get_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM touki_records WHERE id = %s RETURNING id", (record_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Not found")
        conn.commit()
        return {"status": "deleted"}

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
