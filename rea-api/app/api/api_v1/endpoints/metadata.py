"""
データベースメタデータAPI
テーブル構造、カラム情報、ラベル情報を提供

選択肢の取得:
- master_optionsテーブル（source='rea'）から取得
- master_category_codeでカテゴリを指定
"""
from typing import Any, Dict, List, Optional, Set

from app.api import dependencies
from app.core.database import engine
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import MetaData, Table, text
from sqlalchemy.orm import Session

router = APIRouter()

# SQLインジェクション対策: 許可テーブルのホワイトリスト
ALLOWED_TABLES: Set[str] = {
    "properties", "building_info", "land_info", "property_images",
    "property_locations", "property_registries", "amenities",
    "column_labels", "master_categories", "master_options",
    "m_facilities", "m_stations", "m_postal_codes",
}

# 表示順序のデフォルト値（システム/非表示グループ用）
DEFAULT_ORDER: int = 999


@router.get("/tables", response_model=List[Dict[str, Any]])
def get_all_tables(db: Session = Depends(dependencies.get_db)) -> List[Dict[str, Any]]:
    """
    全テーブル一覧を取得
    """
    try:
        query = text(
            """
            SELECT 
                t.table_name,
                t.table_type,
                obj_description(c.oid) as table_comment,
                (
                    SELECT COUNT(*)
                    FROM information_schema.columns col
                    WHERE col.table_name = t.table_name
                    AND col.table_schema = 'public'
                ) as column_count,
                (
                    SELECT COUNT(*)::int
                    FROM information_schema.table_constraints tc
                    WHERE tc.table_name = t.table_name
                    AND tc.constraint_type = 'PRIMARY KEY'
                ) as has_primary_key
            FROM information_schema.tables t
            JOIN pg_class c ON c.relname = t.table_name
            WHERE t.table_schema = 'public'
            AND t.table_type = 'BASE TABLE'
            ORDER BY t.table_name
        """
        )

        result = db.execute(query)
        tables = []
        for row in result:
            tables.append(
                {
                    "table_name": row.table_name,
                    "table_type": row.table_type,
                    "table_comment": row.table_comment,
                    "column_count": row.column_count,
                    "has_primary_key": bool(row.has_primary_key),
                }
            )

        return tables

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/{table_name}", response_model=Dict[str, Any])
def get_table_details(
    table_name: str, db: Session = Depends(dependencies.get_db)
) -> Dict[str, Any]:
    """
    特定テーブルの詳細情報を取得
    """
    try:
        # テーブル存在確認
        check_query = text(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = :table_name
            )
        """
        )
        exists = db.execute(check_query, {"table_name": table_name}).scalar()

        if not exists:
            raise HTTPException(
                status_code=404, detail=f"Table '{table_name}' not found"
            )

        # テーブル情報取得
        table_info_query = text(
            """
            SELECT 
                t.table_name,
                obj_description(c.oid) as table_comment,
                (
                    SELECT COUNT(*)::int
                    FROM :table_name
                ) as record_count
            FROM information_schema.tables t
            JOIN pg_class c ON c.relname = t.table_name
            WHERE t.table_schema = 'public'
            AND t.table_name = :table_name
        """
        )

        # カラム情報取得
        columns_query = text(
            """
            SELECT 
                c.column_name,
                c.data_type,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                c.is_nullable,
                c.column_default,
                c.ordinal_position,
                col_description(pgc.oid, c.ordinal_position) as column_comment,
                CASE 
                    WHEN pk.column_name IS NOT NULL THEN true 
                    ELSE false 
                END as is_primary_key,
                CASE 
                    WHEN fk.column_name IS NOT NULL THEN true 
                    ELSE false 
                END as is_foreign_key,
                fk.foreign_table_name,
                fk.foreign_column_name
            FROM information_schema.columns c
            JOIN pg_class pgc ON pgc.relname = c.table_name
            LEFT JOIN (
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = :table_name
                AND tc.constraint_type = 'PRIMARY KEY'
            ) pk ON pk.column_name = c.column_name
            LEFT JOIN (
                SELECT 
                    kcu.column_name,
                    ccu.table_name as foreign_table_name,
                    ccu.column_name as foreign_column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name
                WHERE tc.table_name = :table_name
                AND tc.constraint_type = 'FOREIGN KEY'
            ) fk ON fk.column_name = c.column_name
            WHERE c.table_schema = 'public'
            AND c.table_name = :table_name
            ORDER BY c.ordinal_position
        """
        )

        columns_result = db.execute(columns_query, {"table_name": table_name})
        columns = []

        for col in columns_result:
            column_info = {
                "column_name": col.column_name,
                "data_type": col.data_type,
                "character_maximum_length": col.character_maximum_length,
                "numeric_precision": col.numeric_precision,
                "numeric_scale": col.numeric_scale,
                "is_nullable": col.is_nullable == "YES",
                "column_default": col.column_default,
                "ordinal_position": col.ordinal_position,
                "column_comment": col.column_comment,
                "is_primary_key": col.is_primary_key,
                "is_foreign_key": col.is_foreign_key,
                "foreign_table_name": col.foreign_table_name,
                "foreign_column_name": col.foreign_column_name,
            }
            columns.append(column_info)

        # レコード数取得（ホワイトリスト検証済みのテーブルのみ）
        if table_name in ALLOWED_TABLES:
            count_query = text(f"SELECT COUNT(*)::int FROM {table_name}")
            record_count = db.execute(count_query).scalar()
        else:
            record_count = None  # 許可外テーブルはカウントしない

        return {
            "table_name": table_name,
            "record_count": record_count,
            "columns": columns,
            "column_count": len(columns),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/columns/{table_name}", response_model=List[Dict[str, Any]])
def get_table_columns_with_labels(
    table_name: str, db: Session = Depends(dependencies.get_db)
) -> List[Dict[str, Any]]:
    """
    テーブルのカラム情報をラベル付きで取得
    column_labelsテーブルの情報も結合
    仮想カラム（DBに存在しないがcolumn_labelsに定義されているカラム）も含む

    選択肢の取得:
    - property_type → property_typesテーブル
    - その他 → master_options (source='rea') から取得（master_category_codeで指定）
    """
    try:
        # master_optionsキャッシュを先に取得
        master_options_cache = _get_master_options_cache(db)

        # 1. DBカラム + column_labels（column_labelsに登録されているカラムのみ表示）
        query = text(
            """
            SELECT
                c.column_name,
                c.data_type,
                c.character_maximum_length,
                c.numeric_precision,
                c.is_nullable,
                c.column_default,
                c.ordinal_position,
                -- column_labelsからの情報
                cl.japanese_label,
                cl.description,
                cl.input_type,
                cl.display_order,
                cl.is_required,
                cl.group_name,
                cl.max_length,
                cl.visible_for,
                cl.master_category_code,
                cl.group_order,
                -- 主キー判定
                CASE
                    WHEN pk.column_name IS NOT NULL THEN true
                    ELSE false
                END as is_primary_key
            FROM information_schema.columns c
            INNER JOIN column_labels cl
                ON cl.table_name = c.table_name
                AND cl.column_name = c.column_name
            LEFT JOIN (
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = :table_name
                AND tc.constraint_type = 'PRIMARY KEY'
            ) pk ON pk.column_name = c.column_name
            WHERE c.table_schema = 'public'
            AND c.table_name = :table_name
            ORDER BY
                COALESCE(cl.group_order, 999),
                COALESCE(cl.display_order, c.ordinal_position),
                c.ordinal_position
        """
        )

        result = db.execute(query, {"table_name": table_name})
        columns = []
        existing_column_names = set()

        # property_typesから動的に選択肢を取得
        property_type_options = _get_property_type_options(db)

        for row in result:
            existing_column_names.add(row.column_name)

            # 選択肢の取得:
            # 1. property_type → property_typesテーブル
            # 2. その他 → master_options (source='rea')
            if row.column_name == "property_type":
                options = property_type_options
            elif row.master_category_code and row.master_category_code in master_options_cache:
                # master_optionsから取得（コード:ラベル形式で返す）
                options = master_options_cache[row.master_category_code]
            else:
                options = None

            column_info = {
                "column_name": row.column_name,
                "data_type": row.data_type,
                "character_maximum_length": row.character_maximum_length,
                "numeric_precision": row.numeric_precision,
                "is_nullable": row.is_nullable == "YES",
                "column_default": row.column_default,
                "ordinal_position": row.ordinal_position,
                "is_primary_key": row.is_primary_key,
                # ラベル情報
                "label_ja": row.japanese_label or row.column_name,  # 日本語ラベルがなければカラム名
                "label_en": row.column_name,  # 英語ラベルは存在しないのでカラム名を使用
                "description": row.description,
                "input_type": row.input_type or _guess_input_type(row.data_type),
                "validation_rules": None,  # 存在しない
                "display_order": row.display_order or row.ordinal_position,
                "is_required": row.is_required
                if row.is_required is not None
                else (row.is_nullable != "YES"),
                "is_searchable": False,  # 存在しない
                "is_display_list": False,  # 存在しない
                "group_name": row.group_name or "基本情報",
                "group_order": row.group_order if row.group_order is not None else DEFAULT_ORDER,
                "placeholder": None,  # 存在しない
                "help_text": row.description,  # descriptionを流用
                "default_value": None,  # 存在しない
                "options": options,  # master_optionsまたはproperty_typesから取得
                "is_virtual": False,  # 実カラム
                "visible_for": row.visible_for,  # 物件種別による表示制御
            }
            columns.append(column_info)

        # 2. 仮想カラム（column_labelsにのみ存在するカラム）を追加
        virtual_query = text(
            """
            SELECT
                cl.column_name,
                cl.japanese_label,
                cl.description,
                cl.input_type,
                cl.display_order,
                cl.is_required,
                cl.group_name,
                cl.max_length,
                cl.data_type,
                cl.visible_for,
                cl.master_category_code,
                cl.group_order
            FROM column_labels cl
            WHERE cl.table_name = :table_name
            AND cl.column_name NOT IN (
                SELECT c.column_name
                FROM information_schema.columns c
                WHERE c.table_schema = 'public' AND c.table_name = :table_name
            )
            ORDER BY cl.group_order, cl.display_order
        """
        )

        virtual_result = db.execute(virtual_query, {"table_name": table_name})
        for row in virtual_result:
            # 仮想カラムのoptions取得（master_optionsから）
            if row.master_category_code and row.master_category_code in master_options_cache:
                virtual_options = master_options_cache[row.master_category_code]
            else:
                virtual_options = None

            column_info = {
                "column_name": row.column_name,
                "data_type": row.data_type or "virtual",
                "character_maximum_length": None,
                "numeric_precision": None,
                "is_nullable": True,
                "column_default": None,
                "ordinal_position": row.display_order or DEFAULT_ORDER,
                "is_primary_key": False,
                "label_ja": row.japanese_label or row.column_name,
                "label_en": row.column_name,
                "description": row.description,
                "input_type": row.input_type or "text",
                "validation_rules": None,
                "display_order": row.display_order or DEFAULT_ORDER,
                "is_required": row.is_required or False,
                "is_searchable": False,
                "is_display_list": False,
                "group_name": row.group_name or "その他",
                "group_order": row.group_order if row.group_order is not None else DEFAULT_ORDER,
                "placeholder": None,
                "help_text": row.description,
                "default_value": None,
                "options": virtual_options,
                "is_virtual": True,  # 仮想カラム
                "visible_for": row.visible_for,  # 物件種別による表示制御
            }
            columns.append(column_info)

        # 実カラムと仮想カラムを合わせてgroup_order, display_orderでソート
        columns.sort(key=lambda c: (c.get('group_order', DEFAULT_ORDER), c.get('display_order', DEFAULT_ORDER)))

        return columns

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/enums/{enum_name}", response_model=List[str])
def get_enum_values(
    enum_name: str, db: Session = Depends(dependencies.get_db)
) -> List[str]:
    """
    ENUM型の値一覧を取得
    """
    try:
        query = text(
            """
            SELECT enumlabel 
            FROM pg_enum e
            JOIN pg_type t ON e.enumtypid = t.oid
            WHERE t.typname = :enum_name
            ORDER BY e.enumsortorder
        """
        )

        result = db.execute(query, {"enum_name": enum_name})
        values = [row.enumlabel for row in result]

        if not values:
            raise HTTPException(
                status_code=404, detail=f"Enum type '{enum_name}' not found"
            )

        return values

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter-options", response_model=Dict[str, Any])
def get_filter_options(db: Session = Depends(dependencies.get_db)) -> Dict[str, Any]:
    """
    フィルター用のオプション一覧を取得（メタデータ駆動）
    master_optionsテーブルから動的に取得
    """
    try:
        filter_options: Dict[str, List[Dict[str, Any]]] = {}

        # column_labelsからフィルター用フィールドのmaster_category_codeを取得
        query = text("""
            SELECT column_name, master_category_code
            FROM column_labels
            WHERE table_name = 'properties'
            AND column_name IN ('sales_status', 'publication_status')
            AND master_category_code IS NOT NULL
        """)
        result = db.execute(query)

        for row in result:
            column_name = row.column_name
            master_category_code = row.master_category_code

            # master_optionsから選択肢を取得（metadataも含む）
            options_query = text("""
                SELECT mo.option_value, mo.metadata
                FROM master_options mo
                JOIN master_categories mc ON mo.category_id = mc.id
                WHERE mc.category_code = :category_code
                AND mo.is_active = true
                ORDER BY mo.display_order
            """)
            options_result = db.execute(options_query, {"category_code": master_category_code})
            import json
            options = []
            for opt_row in options_result:
                opt = {"value": opt_row.option_value, "label": opt_row.option_value}
                if opt_row.metadata:
                    meta = json.loads(opt_row.metadata) if isinstance(opt_row.metadata, str) else opt_row.metadata
                    if 'color' in meta:
                        opt['color'] = meta['color']
                    if 'bg' in meta:
                        opt['bg'] = meta['bg']
                options.append(opt)
            if options:
                filter_options[column_name] = options

        # property_typesテーブルからも取得（簡易版）
        # 注意: valueはid（英語）、labelは日本語ラベル
        # DBのproperty_typeカラムには英語ID（detached等）が入っている
        pt_query = text("""
            SELECT id, label, group_name
            FROM property_types
            ORDER BY
                CASE group_name
                    WHEN '居住用' THEN 1
                    WHEN '事業用' THEN 2
                    WHEN '投資用' THEN 3
                    ELSE 4
                END,
                label
        """)
        pt_result = db.execute(pt_query)
        filter_options["property_type_simple"] = [
            {"value": row.id, "label": row.label, "group": row.group_name}
            for row in pt_result
        ]

        return filter_options

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validation/rules", response_model=Dict[str, Any])
def get_validation_rules() -> Dict[str, Any]:
    """
    利用可能なバリデーションルールの一覧を取得
    """
    return {
        "available_rules": {
            "required": "必須項目",
            "email": "メールアドレス形式",
            "url": "URL形式",
            "phone": "電話番号形式",
            "postal_code": "郵便番号形式",
            "min_length": "最小文字数",
            "max_length": "最大文字数",
            "min_value": "最小値",
            "max_value": "最大値",
            "pattern": "正規表現パターン",
            "date_format": "日付形式",
            "file_types": "許可ファイル形式",
            "file_size": "最大ファイルサイズ",
        },
        "input_types": {
            "text": "テキスト入力",
            "number": "数値入力",
            "email": "メール入力",
            "tel": "電話番号入力",
            "date": "日付選択",
            "datetime": "日時選択",
            "select": "プルダウン選択",
            "radio": "ラジオボタン",
            "checkbox": "チェックボックス",
            "textarea": "複数行テキスト",
            "file": "ファイルアップロード",
            "image": "画像アップロード",
            "hidden": "非表示フィールド",
        },
    }


def _get_property_type_options(db: Session) -> List[Dict[str, str]]:
    """
    property_typesテーブルから物件種別の選択肢を取得
    グループごとにソートして返す
    """
    query = text("""
        SELECT id, label, group_name
        FROM property_types
        ORDER BY
            CASE group_name
                WHEN '居住用' THEN 1
                WHEN '事業用' THEN 2
                WHEN '投資用' THEN 3
                ELSE 4
            END,
            label
    """)
    result = db.execute(query)
    return [
        {"value": row.id, "label": row.label, "group": row.group_name}
        for row in result
    ]


def _guess_input_type(data_type: str) -> str:
    """
    データ型から入力タイプを推測
    """
    type_mapping = {
        "integer": "number",
        "bigint": "number",
        "smallint": "number",
        "numeric": "number",
        "decimal": "number",
        "real": "number",
        "double precision": "number",
        "character varying": "text",
        "character": "text",
        "text": "textarea",
        "boolean": "checkbox",
        "date": "date",
        "timestamp": "datetime",
        "timestamp without time zone": "datetime",
        "timestamp with time zone": "datetime",
        "time": "time",
        "json": "textarea",
        "jsonb": "textarea",
    }

    return type_mapping.get(data_type.lower(), "text")


def _get_master_options_cache(db: Session) -> Dict[str, str]:
    """
    master_optionsからREAソースの選択肢をカテゴリ別に取得
    フロントエンドが期待する形式（コード:ラベル,コード:ラベル...）で返す

    Returns:
        Dict[category_code, "1:ラベル1,2:ラベル2,..."]
    """
    query = text("""
        SELECT
            mc.category_code,
            mo.option_code,
            mo.option_value
        FROM master_options mo
        JOIN master_categories mc ON mo.category_id = mc.id
        WHERE mo.source = 'rea'
        AND mo.is_active = true
        ORDER BY mc.category_code, mo.display_order
    """)
    result = db.execute(query)

    # カテゴリごとにグループ化
    options_by_category: Dict[str, list] = {}
    for row in result:
        if row.category_code not in options_by_category:
            options_by_category[row.category_code] = []
        # option_code は "rea_1" 形式なので、数字部分のみ抽出
        code = row.option_code.replace("rea_", "")
        options_by_category[row.category_code].append(f"{code}:{row.option_value}")

    # カンマ区切り文字列に変換
    return {
        category: ",".join(options)
        for category, options in options_by_category.items()
    }
