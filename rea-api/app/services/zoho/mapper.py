"""
メタデータ駆動インポートマッパー

DBテーブル（import_field_mappings, import_value_mappings）から
マッピング定義を読み込み、ソースデータをREA形式に変換する。

使い回し可能: source_type を変えるだけで他のソース（scraper, csv等）にも対応可能
"""
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from functools import lru_cache


class MetaDrivenMapper:
    """
    メタデータ駆動マッパー

    DBからマッピング定義を読み込み、汎用的な変換を行う。
    source_typeを変えるだけで、ZOHO以外のソースにも対応可能。
    """

    def __init__(self, source_type: str = "zoho"):
        self.source_type = source_type
        self._field_mappings: Optional[List[Dict]] = None
        self._value_mappings: Optional[Dict[str, Dict[str, Tuple[str, Dict]]]] = None
        self._db = None

    def _get_db(self):
        """DB接続を取得（遅延初期化）"""
        if self._db is None:
            from shared.database import READatabase
            self._db = READatabase()
        return self._db

    def load_mappings(self) -> None:
        """DBからマッピング定義を読み込む"""
        db = self._get_db()
        conn = db.get_connection()
        cur = conn.cursor()

        # フィールドマッピング
        cur.execute("""
            SELECT source_field, target_table, target_column, transform_type, transform_config, description
            FROM import_field_mappings
            WHERE source_type = %s AND is_active = true
            ORDER BY display_order
        """, (self.source_type,))

        self._field_mappings = []
        for row in cur.fetchall():
            # PostgreSQLのJSONBはすでにdictとして返される
            config = row[4]
            if isinstance(config, str):
                config = json.loads(config)
            self._field_mappings.append({
                "source_field": row[0],
                "target_table": row[1],
                "target_column": row[2],
                "transform_type": row[3],
                "transform_config": config,
                "description": row[5]
            })

        # 値マッピング（field_name -> source_value -> (target_value, extra_data)）
        cur.execute("""
            SELECT field_name, source_value, target_value, extra_data
            FROM import_value_mappings
            WHERE source_type = %s AND is_active = true
            ORDER BY display_order
        """, (self.source_type,))

        self._value_mappings = {}
        for row in cur.fetchall():
            field_name = row[0]
            source_value = row[1]
            target_value = row[2]
            # PostgreSQLのJSONBはすでにdictとして返される
            extra_data = row[3] if row[3] else {}
            if isinstance(extra_data, str):
                extra_data = json.loads(extra_data)

            if field_name not in self._value_mappings:
                self._value_mappings[field_name] = {}
            self._value_mappings[field_name][source_value] = (target_value, extra_data)

        cur.close()
        conn.close()

    def map_record(self, source_record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        ソースレコードをREA形式に変換

        Args:
            source_record: ソースデータ（ZOHOのレコード等）

        Returns:
            {
                "properties": {...},
                "land_info": {...},
                "building_info": {...},
                "amenities": {...}
            }
        """
        if self._field_mappings is None:
            self.load_mappings()

        result = {
            "properties": {},
            "land_info": {},
            "building_info": {},
            "amenities": {}
        }

        # ソースID保存（ZOHO用）
        if "id" in source_record:
            result["properties"]["zoho_id"] = str(source_record["id"])
            result["properties"]["zoho_synced_at"] = datetime.now()
            result["properties"]["zoho_sync_status"] = "synced"

        # 各フィールドマッピングを適用
        for mapping in self._field_mappings:
            source_field = mapping["source_field"]
            target_table = mapping["target_table"]
            target_column = mapping["target_column"]
            transform_type = mapping["transform_type"]
            transform_config = mapping["transform_config"]

            # ソース値を取得
            source_value = source_record.get(source_field)

            # 変換タイプに応じて処理
            if transform_type == "direct":
                transformed = self._transform_direct(source_value)
            elif transform_type == "value_map":
                transformed, extra = self._transform_value_map(target_column, source_value)
                # extra_dataがあれば適用（例: is_new_construction, sales_status）
                if extra:
                    for key, val in extra.items():
                        if key.startswith("is_"):
                            result["properties"][key] = val
                        elif key == "sales_status":
                            result["properties"]["sales_status"] = val
            elif transform_type == "numeric":
                transformed = self._transform_numeric(source_value)
            elif transform_type == "composite":
                transformed = self._transform_composite(source_record, transform_config)
            elif transform_type == "date_composite":
                transformed = self._transform_date_composite(source_record, transform_config)
            elif transform_type == "object_extract":
                transformed = self._transform_object_extract(source_value, transform_config)
            elif transform_type == "derived_flag":
                # フラグは value_map で処理されるのでスキップ
                continue
            else:
                transformed = source_value

            # 結果に格納
            if transformed is not None and target_table in result:
                result[target_table][target_column] = transformed

        return result

    def _transform_direct(self, value: Any) -> Any:
        """そのまま返す（NULLチェックのみ）"""
        if value is None or value == "":
            return None
        return value

    def _transform_value_map(self, field_name: str, value: Any) -> Tuple[Any, Dict]:
        """値マッピングを適用"""
        # 空文字・NULLもマッピング対象（import_value_mappingsに登録されていれば変換）
        str_value = str(value).strip() if value is not None else ""

        if field_name in self._value_mappings:
            mapping = self._value_mappings[field_name]
            if str_value in mapping:
                target, extra = mapping[str_value]
                # code:label形式の場合、DBに保存するのはcodeのみ
                # （DBカラムがinteger型の場合に対応）
                if target and ':' in str(target):
                    target = target.split(':')[0]
                return target, extra

        # マッピングが見つからない場合はNone
        return None, {}

    def _transform_numeric(self, value: Any) -> Optional[float]:
        """数値変換"""
        if value is None or value == "":
            return None

        try:
            if isinstance(value, str):
                # カンマ、単位を除去
                value = value.replace(",", "").replace("円", "").replace("¥", "")
                value = value.replace("㎡", "").replace("m2", "").replace("%", "")
            return float(value)
        except (ValueError, TypeError):
            return None

    def _transform_composite(self, record: Dict, config: Dict) -> Any:
        """複合フィールド変換"""
        if not config:
            return None

        composite_type = config.get("type")

        if composite_type == "address":
            # 住所結合: 町名 + 住居表示/地番
            fields = config.get("fields", [])
            town = record.get(fields[0], "") or "" if len(fields) > 0 else ""
            street = record.get(fields[1], "") or "" if len(fields) > 1 else ""
            chiban = record.get(fields[2], "") or "" if len(fields) > 2 else ""

            address_number = street if street else chiban

            if town and address_number:
                if "丁目" in town and "丁目" in address_number:
                    return address_number if address_number[0].isdigit() else f"{town}{address_number}"
                return f"{town}{address_number}"
            return address_number or town or None

        elif composite_type == "road_info":
            # 道路情報JSONB
            fields_map = config.get("fields", {})
            road_info = {}

            for key, source_field in fields_map.items():
                value = record.get(source_field)
                if value:
                    # 値マッピングが必要な場合
                    if key in ["road_access", "road1_type", "road2_type"]:
                        mapped, _ = self._transform_value_map(key.replace("road1_", "road_").replace("road2_", "road_"), value)
                        road_info[key] = mapped if mapped else value
                    elif key in ["road1_direction", "road2_direction"]:
                        mapped, _ = self._transform_value_map("direction", value)
                        road_info[key] = mapped if mapped else value
                    elif key in ["road1_width", "road2_width", "road1_frontage", "road2_frontage"]:
                        road_info[key] = self._transform_numeric(value)
                    else:
                        road_info[key] = value

            return road_info if road_info else None

        return None

    def _transform_date_composite(self, record: Dict, config: Dict) -> Optional[str]:
        """日付複合変換（年+月）"""
        if not config:
            return None

        year_field = config.get("year_field")
        month_field = config.get("month_field")

        year = record.get(year_field)
        month = record.get(month_field)

        if year:
            try:
                y = int(year)
                m = int(month) if month else 1
                return f"{y}-{m:02d}-01"
            except (ValueError, TypeError):
                pass

        return None

    def _transform_object_extract(self, value: Any, config: Dict) -> Any:
        """オブジェクトからキー抽出"""
        if not value or not config:
            return None

        key = config.get("key")
        if isinstance(value, dict) and key:
            return value.get(key)

        return None

    def get_mapping_stats(self) -> Dict[str, Any]:
        """マッピング統計を取得"""
        if self._field_mappings is None:
            self.load_mappings()

        return {
            "source_type": self.source_type,
            "field_mappings_count": len(self._field_mappings),
            "value_mappings_count": sum(len(v) for v in self._value_mappings.values()),
            "value_mapping_fields": list(self._value_mappings.keys())
        }

    def validate_mappings(self) -> Dict[str, Any]:
        """
        マッピングの整合性をチェック

        Returns:
            {
                "valid": bool,
                "errors": [...],
                "warnings": [...]
            }
        """
        if self._field_mappings is None:
            self.load_mappings()

        errors = []
        warnings = []

        db = self._get_db()
        conn = db.get_connection()
        cur = conn.cursor()

        # master_optionsの全オプションを取得
        cur.execute("""
            SELECT mc.category_code, mo.option_code, mo.option_value
            FROM master_options mo
            JOIN master_categories mc ON mo.category_id = mc.id
            WHERE mo.is_active = true
        """)
        valid_options = {}
        for row in cur.fetchall():
            category = row[0]
            if category not in valid_options:
                valid_options[category] = {}
            valid_options[category][row[1]] = row[2]  # code -> value

        # property_typesテーブルから有効なIDを取得（別マスター）
        cur.execute("SELECT id, label FROM property_types")
        property_type_ids = {}
        for row in cur.fetchall():
            property_type_ids[row[0]] = row[1]  # id -> label

        # 各value_mappingのtarget_valueをチェック
        for field_name, mappings in self._value_mappings.items():
            for source_value, (target_value, extra) in mappings.items():
                # property_typeは別マスター（property_typesテーブル）を使用
                if field_name == 'property_type':
                    if target_value not in property_type_ids:
                        errors.append({
                            "field": field_name,
                            "source_value": source_value,
                            "target_value": target_value,
                            "error": f"'{target_value}' がproperty_typesテーブルに存在しません"
                        })
                    # property_typeはcode:label形式ではないので、警告不要
                    continue

                # code:label形式かチェック
                if ':' in str(target_value):
                    code, label = target_value.split(':', 1)
                    # master_optionsに存在するかチェック
                    if field_name in valid_options:
                        if code not in valid_options[field_name]:
                            errors.append({
                                "field": field_name,
                                "source_value": source_value,
                                "target_value": target_value,
                                "error": f"code '{code}' がmaster_options ({field_name}) に存在しません"
                            })
                        elif valid_options[field_name][code] != label:
                            warnings.append({
                                "field": field_name,
                                "source_value": source_value,
                                "target_value": target_value,
                                "warning": f"labelが一致しません: master_options='{valid_options[field_name][code]}', mapping='{label}'"
                            })
                else:
                    # code:label形式でない場合は警告
                    warnings.append({
                        "field": field_name,
                        "source_value": source_value,
                        "target_value": target_value,
                        "warning": "code:label形式ではありません（推奨形式: 'code:label'）"
                    })

        cur.close()
        conn.close()

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "checked_fields": list(self._value_mappings.keys())
        }

    def validate_record(self, source_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        レコードのマッピング結果を事前検証（ドライラン）

        Returns:
            {
                "valid": bool,
                "mapped_data": {...},
                "errors": [...],
                "warnings": [...]
            }
        """
        errors = []
        warnings = []

        # マッピング実行
        try:
            mapped_data = self.map_record(source_record)
        except Exception as e:
            return {
                "valid": False,
                "mapped_data": None,
                "errors": [{"error": str(e)}],
                "warnings": []
            }

        # 必須フィールドのチェック
        required_fields = ['property_type', 'property_name']
        for field in required_fields:
            if not mapped_data.get('properties', {}).get(field):
                warnings.append({
                    "field": field,
                    "warning": f"必須フィールド '{field}' が空です"
                })

        # 数値フィールドの妥当性チェック
        price = mapped_data.get('properties', {}).get('price')
        if price is not None and (price < 0 or price > 100000000000):
            warnings.append({
                "field": "price",
                "value": price,
                "warning": "価格が異常値です"
            })

        land_area = mapped_data.get('land_info', {}).get('land_area')
        if land_area is not None and (land_area < 0 or land_area > 1000000):
            warnings.append({
                "field": "land_area",
                "value": land_area,
                "warning": "土地面積が異常値です"
            })

        return {
            "valid": len(errors) == 0,
            "mapped_data": mapped_data,
            "errors": errors,
            "warnings": warnings
        }


# ZOHO用シングルトンインスタンス
zoho_mapper = MetaDrivenMapper(source_type="zoho")


# 後方互換性のため、旧ZohoMapperクラスも残す
class ZohoMapper(MetaDrivenMapper):
    """ZOHO専用マッパー（後方互換性用）"""

    def __init__(self):
        super().__init__(source_type="zoho")


class ReverseMapper:
    """
    逆マッピング: REA → ZOHO

    REAのデータをZOHO形式に変換してエクスポートする。
    import_field_mappings, import_value_mappingsを逆引きする。
    """

    def __init__(self, target_type: str = "zoho"):
        self.target_type = target_type
        self._reverse_field_mappings: Optional[Dict[str, Dict]] = None
        self._reverse_value_mappings: Optional[Dict[str, Dict[str, str]]] = None
        self._db = None

    def _get_db(self):
        if self._db is None:
            from shared.database import READatabase
            self._db = READatabase()
        return self._db

    def load_mappings(self) -> None:
        """DBから逆マッピング定義を読み込む"""
        db = self._get_db()
        conn = db.get_connection()
        cur = conn.cursor()

        # フィールドマッピング（逆引き: target_column -> source_field）
        cur.execute("""
            SELECT source_field, target_table, target_column
            FROM import_field_mappings
            WHERE source_type = %s AND is_active = true
        """, (self.target_type,))

        self._reverse_field_mappings = {}
        for row in cur.fetchall():
            source_field = row[0]
            target_table = row[1]
            target_column = row[2]
            key = f"{target_table}.{target_column}"
            self._reverse_field_mappings[key] = {
                "zoho_field": source_field,
                "table": target_table,
                "column": target_column
            }

        # 値マッピング（逆引き: target_value -> source_value）
        cur.execute("""
            SELECT field_name, source_value, target_value
            FROM import_value_mappings
            WHERE source_type = %s AND is_active = true
        """, (self.target_type,))

        self._reverse_value_mappings = {}
        for row in cur.fetchall():
            field_name = row[0]
            source_value = row[1]
            target_value = row[2]

            # target_valueからコード部分を抽出（例: "1:木造" -> "1"）
            code = target_value.split(":")[0] if ":" in target_value else target_value

            if field_name not in self._reverse_value_mappings:
                self._reverse_value_mappings[field_name] = {}
            # REAのcode -> ZOHOのsource_value
            self._reverse_value_mappings[field_name][code] = source_value

        cur.close()
        conn.close()

    def reverse_map_record(self, rea_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        REAデータをZOHO形式に変換

        Args:
            rea_data: REAの物件データ（properties + land_info + building_info等を統合したもの）

        Returns:
            ZOHO APIに送信できる形式のデータ
        """
        if self._reverse_field_mappings is None:
            self.load_mappings()

        zoho_data = {}

        # テーブル別に処理
        tables = ["properties", "land_info", "building_info"]

        for table in tables:
            table_data = rea_data.get(table, {})
            if not table_data:
                # rea_dataが統合済みの場合（table名なしでフラット）
                table_data = rea_data

            for column, value in table_data.items():
                if value is None:
                    continue

                key = f"{table}.{column}"
                mapping = self._reverse_field_mappings.get(key)

                if mapping:
                    zoho_field = mapping["zoho_field"]

                    # 値の逆変換
                    if column in self._reverse_value_mappings:
                        str_value = str(value)
                        zoho_value = self._reverse_value_mappings[column].get(str_value, value)
                    else:
                        zoho_value = value

                    zoho_data[zoho_field] = zoho_value

        return zoho_data

    def get_stats(self) -> Dict[str, Any]:
        """マッピング統計"""
        if self._reverse_field_mappings is None:
            self.load_mappings()

        return {
            "target_type": self.target_type,
            "field_mappings_count": len(self._reverse_field_mappings),
            "value_mappings_count": sum(len(v) for v in self._reverse_value_mappings.values())
        }


# ZOHO逆マッピング用シングルトン
zoho_reverse_mapper = ReverseMapper(target_type="zoho")
