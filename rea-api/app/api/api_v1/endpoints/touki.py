"""
登記事項証明書インポートAPI

リファクタリング: 2025-12-15
- コンテキストマネージャー使用
- カスタム例外使用
"""
import json
import logging
import os
import re
import sys
from datetime import date, datetime, timezone
from typing import List, Optional

logger = logging.getLogger(__name__)

from fastapi import APIRouter, File, Query, UploadFile
from pydantic import BaseModel

from app.core.exceptions import DatabaseError, ResourceNotFound, ValidationError
from shared.database import READatabase

# パーサーのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'rea-scraper'))

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
    touki_record_ids: Optional[List[int]] = None


class LinkToukiRequest(BaseModel):
    property_id: int
    touki_record_id: int
    link_type: str = "main_land"


# ========== ヘルパー関数 ==========

def map_structure_to_enum(structure: str) -> str:
    """登記の構造文字列をbuilding_structure_enumにマッピング"""
    if not structure:
        return '9:その他'
    structure = structure.lower()
    if '木造' in structure or 'もくぞう' in structure:
        return '1:木造'
    if 'src' in structure or '鉄骨鉄筋コンクリート' in structure:
        return '4:SRC造'
    if 'rc' in structure or '鉄筋コンクリート' in structure:
        return '3:RC造'
    if '軽量鉄骨' in structure:
        return '5:軽量鉄骨'
    if '鉄骨' in structure:
        return '2:鉄骨造'
    if 'alc' in structure:
        return '6:ALC'
    return '9:その他'


def simple_parse(raw_text: str) -> dict:
    """改良版パース（登記情報提供サービスPDF対応）"""
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
        'parsed_at': datetime.now(timezone.utc).isoformat()
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
        matches = re.findall(r'所\s*在[│\|]([^│┃\n]+)', raw_text)
        for loc in reversed(matches):
            loc = loc.strip()
            if loc and not re.search(r'年|月|日|変更|登記', loc):
                result['land_info']['location'] = loc
                break

        match = re.search(r'([０-９\d]+番[０-９\d]*)\s*│', raw_text)
        if match:
            result['land_info']['lot_number'] = normalize(match.group(1))

        for cat in ['宅地', '畑', '田', '山林', '原野', '雑種地']:
            if f'│{cat}' in raw_text or f'│ {cat}' in raw_text:
                result['land_info']['land_category'] = cat

        area_matches = re.findall(r'│\s*([０-９\d]+)[：:]([０-９\d]+)\s*│', raw_text)
        if area_matches:
            whole, decimal = area_matches[-1]
            area = float(normalize(whole)) + float(normalize(decimal)) / 100
            result['land_info']['land_area_m2'] = round(area, 2)

    # 建物情報
    if result['document_type'] in ['building', 'both']:
        matches = re.findall(r'所\s*在[│\|]([^│┃\n]+)', raw_text)
        for loc in reversed(matches):
            loc = loc.strip()
            if loc and not re.search(r'年|月|日|変更|登記', loc):
                result['building_info']['location'] = loc
                break

        match = re.search(r'家屋番号[│\|]\s*([^│┃\n]+)', raw_text)
        if match:
            result['building_info']['building_number'] = normalize(match.group(1).strip())

        if '居宅' in raw_text:
            result['building_info']['building_type'] = '居宅'

        match = re.search(r'│(木造[^│\n]+階)', raw_text)
        if match:
            result['building_info']['structure'] = match.group(1) + '建'

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

        match = re.search(r'(昭和|平成|令和)([０-９\d]+)年([０-９\d]+)月([０-９\d]+)日新築', raw_text)
        if match:
            era, y, m, d = match.groups()
            era_start = {'昭和': 1926, '平成': 1989, '令和': 2019}
            year = era_start.get(era, 1926) + int(normalize(y)) - 1
            result['building_info']['construction_date'] = f"{year}-{int(normalize(m)):02d}-{int(normalize(d)):02d}"

    # 所有者
    owner_blocks = []
    lines = raw_text.split('\n')
    for i, line in enumerate(lines):
        if '所有者' in line and '登記名義人' not in line:
            addr_match = re.search(r'所有者\s+([^┃\n]+)', line)
            if addr_match:
                address = addr_match.group(1).strip().rstrip('│')
                for offset in range(1, 4):
                    if i + offset >= len(lines):
                        break
                    check_line = lines[i + offset]
                    name_match = re.search(r'[│┃]\s*([^│┃\d０-９\n]{2,})\s*┃', check_line)
                    if not name_match:
                        name_match = re.search(r'^\s*([^\d０-９│┃\n]{2,})\s*┃$', check_line)
                    if name_match:
                        name = re.sub(r'\s+', '', name_match.group(1).strip())
                        skip_words = ['移記', '登記', '原因', '売買', '相続', '平成', '昭和', '令和', '順位']
                        if name and len(name) >= 2 and not any(w in name for w in skip_words):
                            owner_blocks.append({'address': address, 'name': name})
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


def save_to_touki_records(cur, import_id: int, parsed_data: dict) -> List[int]:
    """パース結果をtouki_recordsに保存"""
    record_ids = []
    doc_type = parsed_data.get('document_type', 'unknown')

    owner_info = parsed_data.get('owner_info', {})
    owners = []
    if owner_info.get('owner_name'):
        owners.append({
            'name': owner_info.get('owner_name'),
            'address': owner_info.get('owner_address')
        })

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
            floor_areas = building.get('floor_areas', {})
            construction_date = None
            if building.get('construction_date'):
                try:
                    construction_date = datetime.strptime(
                        building['construction_date'], '%Y-%m-%d'
                    ).date()
                except ValueError as e:
                    logger.warning(f"Invalid construction_date format: {building.get('construction_date')} - {e}")

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


# ========== エンドポイント ==========

@router.post("/upload", response_model=ToukiImportResponse)
async def upload_touki_pdf(file: UploadFile = File(...)):
    """登記事項証明書PDFをアップロードしてテキスト抽出"""
    if not file.filename.lower().endswith('.pdf'):
        raise ValidationError("file", "PDFファイルのみ対応しています")

    if pdfplumber is None:
        raise DatabaseError("pdfplumber not installed")

    # ファイル保存
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
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
    with READatabase.cursor(commit=True) as (cur, conn):
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
        return ToukiImportResponse(
            id=row[0],
            file_name=file.filename,
            status='uploaded' if raw_text else 'error',
            raw_text=raw_text,
            error_message=error_message,
            created_at=row[1]
        )


@router.get("/list", response_model=ToukiListResponse)
async def list_touki_imports(
    status: Optional[str] = Query(None, description="フィルタ: uploaded/parsed/imported/error"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """インポート一覧を取得"""
    with READatabase.cursor() as (cur, conn):
        # カウント
        count_sql = "SELECT COUNT(*) FROM touki_imports WHERE deleted_at IS NULL"
        if status:
            count_sql += " AND status = %s"
            cur.execute(count_sql, (status,))
        else:
            cur.execute(count_sql)
        total = cur.fetchone()[0]

        # データ取得
        sql = """
            SELECT id, file_name, status, raw_text, parsed_data, error_message, created_at
            FROM touki_imports
            WHERE deleted_at IS NULL
        """
        params = []
        if status:
            sql += " AND status = %s"
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
                raw_text=row[3][:500] if row[3] else None,
                parsed_data=row[4],
                error_message=row[5],
                created_at=row[6]
            )
            for row in rows
        ]

        return ToukiListResponse(items=items, total=total)


@router.get("/{import_id}", response_model=ToukiImportResponse)
async def get_touki_import(import_id: int):
    """インポート詳細を取得"""
    with READatabase.cursor() as (cur, conn):
        cur.execute("""
            SELECT id, file_name, status, raw_text, parsed_data, error_message, created_at
            FROM touki_imports
            WHERE id = %s AND deleted_at IS NULL
        """, (import_id,))

        row = cur.fetchone()
        if not row:
            raise ResourceNotFound("登記インポート", import_id)

        return ToukiImportResponse(
            id=row[0],
            file_name=row[1],
            status=row[2],
            raw_text=row[3],
            parsed_data=row[4],
            error_message=row[5],
            created_at=row[6]
        )


@router.post("/{import_id}/parse")
async def parse_touki_import(import_id: int):
    """アップロード済みのテキストをパースして構造化し、touki_recordsに保存"""
    with READatabase.cursor(commit=True) as (cur, conn):
        cur.execute("SELECT raw_text FROM touki_imports WHERE id = %s AND deleted_at IS NULL", (import_id,))
        row = cur.fetchone()
        if not row:
            raise ResourceNotFound("登記インポート", import_id)

        raw_text = row[0]
        if not raw_text:
            raise ValidationError("raw_text", "パース対象のテキストがありません")

        # パーサーをインポート
        try:
            from src.parsers.touki.touki_parser import ToukiParser
            parser = ToukiParser()
            parsed_data = parser.parse(raw_text)
        except ImportError:
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

        return {
            "status": "success",
            "parsed_data": parsed_data,
            "touki_record_ids": touki_record_ids
        }


# ========== touki_records エンドポイント ==========

@router.get("/records/list", response_model=ToukiRecordListResponse)
async def list_touki_records(
    document_type: Optional[str] = Query(None, description="land/building/unit"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """登記レコード一覧"""
    with READatabase.cursor() as (cur, conn):
        count_sql = "SELECT COUNT(*) FROM touki_records WHERE deleted_at IS NULL"
        params = []
        if document_type:
            count_sql += " AND document_type = %s"
            params.append(document_type)
        cur.execute(count_sql, params)
        total = cur.fetchone()[0]

        sql = """
            SELECT id, real_estate_number, document_type, location,
                   lot_number, land_category, land_area_m2,
                   building_number, building_type, structure,
                   floor_area_m2, floor_areas, construction_date,
                   owners, mortgages, touki_import_id, created_at
            FROM touki_records
            WHERE deleted_at IS NULL
        """
        params = []
        if document_type:
            sql += " AND document_type = %s"
            params.append(document_type)
        sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(sql, params)
        rows = cur.fetchall()

        items = [
            ToukiRecordResponse(
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
            for row in rows
        ]

        return ToukiRecordListResponse(items=items, total=total)


@router.get("/records/{record_id}", response_model=ToukiRecordResponse)
async def get_touki_record(record_id: int):
    """登記レコード詳細"""
    with READatabase.cursor() as (cur, conn):
        cur.execute("""
            SELECT id, real_estate_number, document_type, location,
                   lot_number, land_category, land_area_m2,
                   building_number, building_type, structure,
                   floor_area_m2, floor_areas, construction_date,
                   owners, mortgages, touki_import_id, created_at
            FROM touki_records WHERE id = %s AND deleted_at IS NULL
        """, (record_id,))

        row = cur.fetchone()
        if not row:
            raise ResourceNotFound("登記レコード", record_id)

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


@router.post("/records/create-property")
async def create_property_from_touki(request: CreatePropertyFromToukiRequest):
    """登記レコードから物件を作成"""
    record_ids = request.touki_record_ids or []
    if request.land_touki_record_id:
        record_ids.append(request.land_touki_record_id)
    if request.building_touki_record_id:
        record_ids.append(request.building_touki_record_id)

    if not record_ids:
        raise ValidationError("touki_record_ids", "登記レコードIDが必要です")

    logger.info(f"create_property_from_touki: record_ids={record_ids}")

    with READatabase.cursor(commit=True) as (cur, conn):
        land_records = []
        building_records = []

        # 登記レコード一括取得
        placeholders = ','.join(['%s'] * len(record_ids))
        cur.execute(f"""
            SELECT id, real_estate_number, document_type, location,
                   lot_number, land_category, land_area_m2,
                   building_number, building_type, structure,
                   floor_area_m2, floor_areas, construction_date, owners
            FROM touki_records WHERE id IN ({placeholders}) AND deleted_at IS NULL
        """, tuple(record_ids))
        rows = cur.fetchall()

        # 存在しないIDのチェック
        found_ids = {row[0] for row in rows}
        for rid in record_ids:
            if rid not in found_ids:
                raise ResourceNotFound("登記レコード", rid)

        for row in rows:
            rec = {
                'id': row[0], 'real_estate_number': row[1], 'document_type': row[2],
                'location': row[3], 'lot_number': row[4], 'land_category': row[5],
                'land_area_m2': row[6], 'building_number': row[7], 'building_type': row[8],
                'structure': row[9], 'floor_area_m2': row[10], 'floor_areas': row[11],
                'construction_date': row[12], 'owners': row[13] or []
            }

            if rec['document_type'] == 'land':
                land_records.append(rec)
            else:
                building_records.append(rec)

        # 物件タイプ判定
        if building_records and land_records:
            property_type = '中古戸建'
        elif building_records:
            property_type = '中古戸建'
        else:
            property_type = '売地'

        # 所在地（建物優先）
        location = ''
        if building_records:
            location = building_records[0]['location']
        elif land_records:
            location = land_records[0]['location']

        # 所有者情報
        owners = []
        if building_records and building_records[0]['owners']:
            owners = building_records[0]['owners']
        elif land_records and land_records[0]['owners']:
            owners = land_records[0]['owners']

        owner_name = owners[0]['name'] if owners else None
        owner_address = owners[0].get('address') if owners else None

        # remarks
        remarks_parts = []
        if owner_name:
            remarks_parts.append(f"所有者: {owner_name}")
            if owner_address:
                remarks_parts.append(f"住所: {owner_address}")
        if land_records:
            remarks_parts.append(f"土地{len(land_records)}筆")
        if building_records:
            remarks_parts.append(f"建物{len(building_records)}棟")

        # 土地面積合計
        total_land_area = sum(r['land_area_m2'] or 0 for r in land_records)

        # propertiesに挿入
        cur.execute("""
            INSERT INTO properties (
                property_name, property_type, address, remarks,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (
            location,
            property_type,
            location,
            '\n'.join(remarks_parts)
        ))
        property_id = cur.fetchone()[0]
        logger.info(f"create_property_from_touki: property created id={property_id}, type={property_type}")

        # land_info
        if land_records:
            chiban_list = ', '.join(r['lot_number'] or '' for r in land_records if r['lot_number'])
            land_category = land_records[0]['land_category']

            cur.execute("""
                INSERT INTO land_info (
                    property_id, chiban, land_category, land_area, address
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                property_id,
                chiban_list,
                land_category,
                total_land_area,
                land_records[0]['location']
            ))
            logger.info(f"create_property_from_touki: land_info created for property_id={property_id}")

        # building_info
        if building_records:
            br = building_records[0]
            floors_above = None
            if br['structure']:
                floor_match = re.search(r'(\d+)階', br['structure'])
                if floor_match:
                    floors_above = int(floor_match.group(1))

            structure_enum = map_structure_to_enum(br['structure'])

            cur.execute("""
                INSERT INTO building_info (
                    property_id, building_structure, total_floor_area,
                    construction_date, building_floors_above
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                property_id,
                structure_enum,
                br['floor_area_m2'],
                br['construction_date'],
                floors_above
            ))
            logger.info(f"create_property_from_touki: building_info created for property_id={property_id}")

        logger.info(f"create_property_from_touki: completed property_id={property_id}, land={len(land_records)}, building={len(building_records)}")
        return {
            "status": "success",
            "property_id": property_id,
            "message": f"物件ID {property_id} を作成しました（土地{len(land_records)}筆、建物{len(building_records)}棟）",
            "touki_record_ids": record_ids
        }


class ApplyToukiRequest(BaseModel):
    property_id: int
    touki_record_ids: List[int]


@router.post("/records/apply-to-property")
async def apply_touki_to_property(request: ApplyToukiRequest):
    """登記情報を既存物件に反映（土地・建物情報を上書き更新）"""
    if not request.touki_record_ids:
        raise ValidationError("touki_record_ids", "登記レコードIDが必要です")

    logger.info(f"apply_touki_to_property: property_id={request.property_id}, record_ids={request.touki_record_ids}")

    with READatabase.cursor(commit=True) as (cur, conn):
        # 物件存在確認
        cur.execute("SELECT id FROM properties WHERE id = %s AND deleted_at IS NULL", (request.property_id,))
        if not cur.fetchone():
            raise ResourceNotFound("物件", request.property_id)

        land_records = []
        building_records = []

        # 登記レコード一括取得
        placeholders = ','.join(['%s'] * len(request.touki_record_ids))
        cur.execute(f"""
            SELECT id, real_estate_number, document_type, location,
                   lot_number, land_category, land_area_m2,
                   building_number, building_type, structure,
                   floor_area_m2, floor_areas, construction_date, owners
            FROM touki_records WHERE id IN ({placeholders}) AND deleted_at IS NULL
        """, tuple(request.touki_record_ids))
        rows = cur.fetchall()

        # 存在しないIDのチェック
        found_ids = {row[0] for row in rows}
        for rid in request.touki_record_ids:
            if rid not in found_ids:
                raise ResourceNotFound("登記レコード", rid)

        for row in rows:
            rec = {
                'id': row[0], 'real_estate_number': row[1], 'document_type': row[2],
                'location': row[3], 'lot_number': row[4], 'land_category': row[5],
                'land_area_m2': row[6], 'building_number': row[7], 'building_type': row[8],
                'structure': row[9], 'floor_area_m2': row[10], 'floor_areas': row[11],
                'construction_date': row[12], 'owners': row[13] or []
            }

            if rec['document_type'] == 'land':
                land_records.append(rec)
            else:
                building_records.append(rec)

        # 所有者情報をremarksに追加
        owners = []
        if building_records and building_records[0]['owners']:
            owners = building_records[0]['owners']
        elif land_records and land_records[0]['owners']:
            owners = land_records[0]['owners']

        remarks_parts = []
        if owners:
            owner_name = owners[0].get('name', '')
            owner_address = owners[0].get('address', '')
            if owner_name:
                remarks_parts.append(f"【登記情報】所有者: {owner_name}")
            if owner_address:
                remarks_parts.append(f"住所: {owner_address}")

        # propertiesのremarksを更新（追記）
        if remarks_parts:
            cur.execute("SELECT remarks FROM properties WHERE id = %s AND deleted_at IS NULL", (request.property_id,))
            current_remarks = cur.fetchone()[0] or ''
            new_remarks = current_remarks
            if new_remarks and not new_remarks.endswith('\n'):
                new_remarks += '\n'
            new_remarks += '\n'.join(remarks_parts)
            cur.execute(
                "UPDATE properties SET remarks = %s, updated_at = NOW() WHERE id = %s",
                (new_remarks, request.property_id)
            )
            logger.info(f"apply_touki_to_property: remarks updated for property_id={request.property_id}")

        # land_info更新（登記情報のみ。住所は上書きしない）
        if land_records:
            chiban_list = ', '.join(r['lot_number'] or '' for r in land_records if r['lot_number'])
            total_land_area = sum(r['land_area_m2'] or 0 for r in land_records)
            land_category = land_records[0]['land_category']
            # 注意: 登記の所在（location）は地番であり、住所（address）ではない
            # addressフィールドには触らない

            # 既存レコードがあるか確認
            cur.execute("SELECT id, chiban, land_category, land_area FROM land_info WHERE property_id = %s AND deleted_at IS NULL", (request.property_id,))
            existing = cur.fetchone()
            if existing:
                # 更新（既存値がある場合は上書きしない）
                cur.execute("""
                    UPDATE land_info SET
                        chiban = CASE WHEN chiban IS NULL OR chiban = '' THEN %s ELSE chiban END,
                        land_category = CASE WHEN land_category IS NULL OR land_category = '' THEN %s ELSE land_category END,
                        land_area = CASE WHEN land_area IS NULL THEN %s ELSE land_area END,
                        updated_at = NOW()
                    WHERE property_id = %s
                """, (chiban_list, land_category, total_land_area, request.property_id))
                logger.info(f"apply_touki_to_property: land_info updated for property_id={request.property_id}")
            else:
                # 新規作成（addressは空のまま）
                cur.execute("""
                    INSERT INTO land_info (property_id, chiban, land_category, land_area)
                    VALUES (%s, %s, %s, %s)
                """, (request.property_id, chiban_list, land_category, total_land_area))
                logger.info(f"apply_touki_to_property: land_info created for property_id={request.property_id}")

        # building_info更新（既存値は上書きしない）
        if building_records:
            br = building_records[0]
            floors_above = None
            if br['structure']:
                floor_match = re.search(r'(\d+)階', br['structure'])
                if floor_match:
                    floors_above = int(floor_match.group(1))

            structure_enum = map_structure_to_enum(br['structure'])

            # 既存レコードがあるか確認
            cur.execute("SELECT id FROM building_info WHERE property_id = %s AND deleted_at IS NULL", (request.property_id,))
            if cur.fetchone():
                # 更新（既存値がある場合は上書きしない）
                cur.execute("""
                    UPDATE building_info SET
                        building_structure = CASE WHEN building_structure IS NULL OR building_structure = '' THEN %s ELSE building_structure END,
                        total_floor_area = CASE WHEN total_floor_area IS NULL THEN %s ELSE total_floor_area END,
                        construction_date = CASE WHEN construction_date IS NULL THEN %s ELSE construction_date END,
                        building_floors_above = CASE WHEN building_floors_above IS NULL THEN %s ELSE building_floors_above END,
                        updated_at = NOW()
                    WHERE property_id = %s
                """, (structure_enum, br['floor_area_m2'], br['construction_date'], floors_above, request.property_id))
                logger.info(f"apply_touki_to_property: building_info updated for property_id={request.property_id}")
            else:
                # 新規作成
                cur.execute("""
                    INSERT INTO building_info (property_id, building_structure, total_floor_area, construction_date, building_floors_above)
                    VALUES (%s, %s, %s, %s, %s)
                """, (request.property_id, structure_enum, br['floor_area_m2'], br['construction_date'], floors_above))
                logger.info(f"apply_touki_to_property: building_info created for property_id={request.property_id}")

        # 登記レコード論理削除（一括処理）
        placeholders_del = ','.join(['%s'] * len(request.touki_record_ids))
        cur.execute(f"UPDATE touki_records SET deleted_at = NOW() WHERE id IN ({placeholders_del}) AND deleted_at IS NULL", tuple(request.touki_record_ids))
        logger.info(f"apply_touki_to_property: {len(request.touki_record_ids)} touki_records soft-deleted")

        logger.info(f"apply_touki_to_property: completed property_id={request.property_id}, land={len(land_records)}, building={len(building_records)}")
        return {
            "status": "success",
            "property_id": request.property_id,
            "message": f"物件ID {request.property_id} に登記情報を反映しました（土地{len(land_records)}筆、建物{len(building_records)}棟）",
            "applied_records": len(request.touki_record_ids)
        }


@router.post("/records/link")
async def link_touki_to_property(request: LinkToukiRequest):
    """既存物件に登記レコードを紐付け（リンクのみ、データ更新なし）"""
    with READatabase.cursor(commit=True) as (cur, conn):
        cur.execute("SELECT id FROM properties WHERE id = %s AND deleted_at IS NULL", (request.property_id,))
        if not cur.fetchone():
            raise ResourceNotFound("物件", request.property_id)

        cur.execute("SELECT id FROM touki_records WHERE id = %s AND deleted_at IS NULL", (request.touki_record_id,))
        if not cur.fetchone():
            raise ResourceNotFound("登記レコード", request.touki_record_id)

        cur.execute("""
            INSERT INTO property_touki_links (property_id, touki_record_id, link_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (property_id, touki_record_id) DO UPDATE SET link_type = %s
        """, (request.property_id, request.touki_record_id, request.link_type, request.link_type))

        return {"status": "success", "message": "紐付けました"}


@router.delete("/records/{record_id}")
async def delete_touki_record(record_id: int):
    """登記レコードを論理削除"""
    with READatabase.cursor(commit=True) as (cur, conn):
        cur.execute("UPDATE touki_records SET deleted_at = NOW() WHERE id = %s AND deleted_at IS NULL RETURNING id", (record_id,))
        if not cur.fetchone():
            raise ResourceNotFound("登記レコード", record_id)
        return {"status": "deleted"}


@router.delete("/{import_id}")
async def delete_touki_import(import_id: int):
    """インポートを論理削除（ファイルは保持）"""
    with READatabase.cursor(commit=True) as (cur, conn):
        cur.execute("SELECT id FROM touki_imports WHERE id = %s AND deleted_at IS NULL", (import_id,))
        row = cur.fetchone()
        if not row:
            raise ResourceNotFound("登記インポート", import_id)

        cur.execute("UPDATE touki_imports SET deleted_at = NOW() WHERE id = %s", (import_id,))

        # ファイルは論理削除後も保持（復元可能性のため）
        # 物理削除が必要な場合は別途クリーンアップジョブで対応

        return {"status": "deleted"}
