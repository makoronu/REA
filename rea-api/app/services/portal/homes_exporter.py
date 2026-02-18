"""
HOMES CSV出力サービス

REAの物件データをLIFULL HOME'S CSV形式で出力する
"""

import csv
import io
import os
import yaml
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Dict, List, Any, Optional
from pathlib import Path


class HomesExporter:
    """HOMES CSV出力クラス"""

    def __init__(self, db_connection):
        """
        Args:
            db_connection: データベース接続
        """
        self.conn = db_connection
        self.mapping = self._load_mapping()
        self.master_options = self._load_master_options()
        self.property_type_mapping = self.mapping.get('property_type_mapping', {})
        self.sales_status_mapping = self.mapping.get('sales_status_mapping', {})

    def _load_mapping(self) -> Dict:
        """YAMLマッピング定義を読み込む"""
        # rea-api/app/services/portal/homes_exporter.py から REA/docs/portal へ
        mapping_path = Path(__file__).parent.parent.parent.parent.parent / 'docs' / 'portal' / 'homes_field_mapping.yaml'

        if not mapping_path.exists():
            raise FileNotFoundError(f"マッピングファイルが見つかりません: {mapping_path}")

        with open(mapping_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_master_options(self) -> Dict[str, Dict[int, str]]:
        """master_optionsからホームズコードを取得"""
        cur = self.conn.cursor()

        cur.execute("""
            SELECT mc.category_code, mo.option_code, mo.option_value
            FROM master_options mo
            JOIN master_categories mc ON mo.category_id = mc.id
            WHERE mo.source = 'homes'
        """)

        result = {}
        for row in cur.fetchall():
            category_code = row[0]
            option_code = row[1]
            option_value = row[2]

            if category_code not in result:
                result[category_code] = {}
            result[category_code][option_code] = option_value

        cur.close()
        return result

    def _get_rea_to_homes_code(self, category_code: str, rea_value: Any) -> str:
        """REA値をHOMESコードに変換

        REAではmaster_optionsのoption_code（整数）を保存。
        HOMESでは同じoption_codeを文字列として使用。
        """
        if rea_value is None:
            return ""

        # REAの値（option_code）をそのまま文字列として返す
        # master_optionsにはREA用（source='rea'）とHOMES用（source='homes'）があるが
        # 同じカテゴリで同じコードを使用している
        return str(rea_value)

    def _format_datetime(self, dt: Any) -> str:
        """日時をyyyy/mm/dd hh:mm:ss形式に変換"""
        if dt is None:
            return datetime.now(ZoneInfo('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')
        if isinstance(dt, str):
            return dt
        return dt.strftime('%Y/%m/%d %H:%M:%S')

    def _format_date(self, dt: Any) -> str:
        """日付をyyyy/mm/dd形式に変換"""
        if dt is None:
            # 14日後をデフォルトに
            return (datetime.now(ZoneInfo('Asia/Tokyo')) + timedelta(days=14)).strftime('%Y/%m/%d')
        if isinstance(dt, str):
            return dt
        return dt.strftime('%Y/%m/%d')

    def _format_yyyymm(self, dt: Any) -> str:
        """日付をyyyy/mm形式に変換"""
        if dt is None:
            return ""
        if isinstance(dt, str):
            return dt[:7].replace('-', '/')
        return dt.strftime('%Y/%m')

    def _format_latlon(self, lat: float, lon: float) -> str:
        """緯度経度を度分秒形式に変換"""
        if lat is None or lon is None:
            return ""

        def to_dms(decimal_degrees):
            d = int(decimal_degrees)
            m = int((decimal_degrees - d) * 60)
            s = round((decimal_degrees - d - m/60) * 3600, 3)
            return f"{d}.{m:02d}.{s:06.3f}".rstrip('0').rstrip('.')

        return f"{to_dms(lat)}/{to_dms(lon)}"

    def _get_property_type_code(self, property_type: str, is_new_construction: bool = False) -> str:
        """REA property_type → HOMES 物件種別コード変換"""
        # 新築フラグによる分岐
        if property_type == 'detached':
            return "1201" if is_new_construction else "1202"
        elif property_type == 'apartment' or property_type == 'mansion':
            return "1301" if is_new_construction else "1302"

        return self.property_type_mapping.get(property_type, "1202")  # デフォルト: 中古戸建

    def _convert_property_to_homes(self, property_data: Dict) -> List[str]:
        """物件データをHOMES CSVの1行に変換"""
        result = [''] * 427  # CSV No.1〜426 + 終了マーク

        # マッピング定義に従って変換
        for field_def in self.mapping.get('data', []):
            csv_no = field_def.get('csv_no')
            if csv_no is None:
                continue

            idx = csv_no - 1  # 0-indexed

            # 固定値
            if 'value' in field_def:
                result[idx] = field_def['value']
                continue

            # REAソースからの取得
            rea_source = field_def.get('rea_source')
            value = self._get_value_from_source(property_data, rea_source)

            # フォールバック
            if value is None and 'fallback' in field_def:
                fallback = field_def['fallback']
                if fallback == '+14days':
                    value = datetime.now(ZoneInfo('Asia/Tokyo')) + timedelta(days=14)
                else:
                    value = self._get_value_from_source(property_data, fallback)

            # デフォルト値
            if value is None and 'default' in field_def:
                value = field_def['default']

            # フォーマット変換
            format_type = field_def.get('format')
            if format_type == 'datetime':
                value = self._format_datetime(value)
            elif format_type == 'date':
                value = self._format_date(value)
            elif format_type == 'yyyymm':
                value = self._format_yyyymm(value)
            elif format_type == 'integer':
                value = str(int(value)) if value is not None else ""
            elif format_type == 'decimal':
                value = str(float(value)) if value is not None else ""
            elif format_type == 'latlon' and isinstance(rea_source, list):
                lat = self._get_value_from_source(property_data, rea_source[0])
                lon = self._get_value_from_source(property_data, rea_source[1])
                value = self._format_latlon(lat, lon)

            # マスターカテゴリによるコード変換
            master_category = field_def.get('master_category')
            if master_category and value is not None:
                value = self._get_rea_to_homes_code(master_category, value)

            # 特殊変換
            transform = field_def.get('transform')
            if transform == 'sales_status_to_homes':
                value = self.sales_status_mapping.get(str(value), "1")

            # 結果設定
            result[idx] = str(value) if value is not None else ""

        # 物件種別の特殊処理
        property_type = property_data.get('property_type', 'detached')
        is_new = property_data.get('is_new_construction', False)
        result[6] = self._get_property_type_code(property_type, is_new)  # csv_no=7

        return result

    def _get_value_from_source(self, data: Dict, source: Any) -> Any:
        """ソース指定から値を取得

        source例:
        - "properties.sale_price"
        - "land_info.land_area"
        - "properties.transportation[0].line"
        """
        if source is None:
            return None

        if isinstance(source, list):
            # 複数ソースの場合は最初のものを返す
            return self._get_value_from_source(data, source[0])

        parts = source.split('.')
        current = data

        for part in parts:
            if current is None:
                return None

            # 配列アクセス
            if '[' in part and ']' in part:
                key = part.split('[')[0]
                idx = int(part.split('[')[1].split(']')[0])

                if key and key in current:
                    current = current[key]

                if isinstance(current, list) and len(current) > idx:
                    current = current[idx]
                else:
                    return None
            else:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None

        return current

    def _generate_header_row(self) -> List[str]:
        """ヘッダ行を生成"""
        result = [''] * 9

        for header_def in self.mapping.get('header', []):
            csv_no = header_def.get('csv_no')
            if csv_no is None:
                continue

            idx = csv_no - 1

            # 環境変数から取得
            if 'env_var' in header_def:
                result[idx] = os.environ.get(header_def['env_var'], '')
            elif 'value' in header_def:
                result[idx] = header_def['value']

        return result

    def export_properties(self, property_ids: List[int]) -> bytes:
        """指定した物件をHOMES CSVとして出力

        Args:
            property_ids: 出力する物件IDのリスト

        Returns:
            Shift_JISエンコードされたCSVバイト列
        """
        # 物件データ取得
        properties = self._fetch_properties(property_ids)

        # CSV生成
        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\r\n')

        # ヘッダ行
        writer.writerow(self._generate_header_row())

        # データ行
        for prop in properties:
            row = self._convert_property_to_homes(prop)
            writer.writerow(row)

        # Shift_JISエンコード
        csv_content = output.getvalue()
        return csv_content.encode('shift_jis', errors='replace')

    def _fetch_properties(self, property_ids: List[int]) -> List[Dict]:
        """物件データを取得（JOIN済みの完全データ）"""
        if not property_ids:
            return []

        cur = self.conn.cursor()

        placeholders = ','.join(['%s'] * len(property_ids))

        cur.execute(f"""
            SELECT
                p.*,
                li.land_area, li.building_coverage_ratio, li.floor_area_ratio,
                li.use_district, li.city_planning, li.land_rights, li.setback,
                li.land_area_measurement, li.terrain, li.land_category,
                li.road_info, li.setback_amount,
                bi.construction_date, bi.building_floors_above, bi.building_floors_below,
                bi.total_floor_area, bi.exclusive_area, bi.balcony_area,
                bi.building_structure, bi.direction, bi.room_type,
                bi.building_manager, bi.management_type, bi.management_association,
                bi.room_floor, bi.room_count
            FROM properties p
            LEFT JOIN land_info li ON p.id = li.property_id
            LEFT JOIN building_info bi ON p.id = bi.property_id
            WHERE p.id IN ({placeholders})
        """, property_ids)

        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()

        result = []
        for row in rows:
            prop = dict(zip(columns, row))
            result.append(prop)

        cur.close()
        return result

    def validate_properties(self, property_ids: List[int]) -> Dict[int, List[str]]:
        """物件データのバリデーション

        Args:
            property_ids: チェックする物件IDのリスト

        Returns:
            {property_id: [エラーメッセージリスト]}
        """
        properties = self._fetch_properties(property_ids)
        errors = {}

        required_fields = [
            ('property_name', '物件名'),
            ('sale_price', '価格'),
            ('address', '住所'),
        ]

        for prop in properties:
            prop_errors = []
            prop_id = prop.get('id')

            for field, label in required_fields:
                if not prop.get(field):
                    prop_errors.append(f'{label}が未入力です')

            if prop_errors:
                errors[prop_id] = prop_errors

        return errors
