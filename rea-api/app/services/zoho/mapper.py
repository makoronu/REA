"""
ZOHO CRM データマッピング

ZOHOのフィールド名 → REAのカラム名への変換
"""
from typing import Dict, Any, Optional, List
from datetime import datetime


# ========================================
# ZOHOフィールド → REAカラム マッピング
# ========================================

# propertiesテーブル用
PROPERTIES_MAPPING = {
    "Name": "property_name",
    "field57": "company_property_number",  # 物件番号
    "field3": "sale_price",  # 価格
    "field8": "property_type",  # 物件種別
    "field6": "transaction_type",  # 取引態様
    "field7": "publication_status",  # 公開
    "field24": "current_status",  # 現況
    "field23": "delivery_timing",  # 引渡時期
    "field5": "prefecture",  # 都道府県
    "field4": "city",  # 市町村
    "field16": "address",  # 住居表示
    "field14": "address_detail",  # 町名
    "field18": "latitude",  # 緯度
    "field15": "longitude",  # 経度
    "field46": "elementary_school",  # 小学校区
    "field47": "junior_high_school",  # 中学校区
    "field50": "catch_copy",  # キャッチコピー1
    "field49": "catch_copy2",  # キャッチコピー2
    "field52": "catch_copy3",  # キャッチコピー3
    "field51": "remarks",  # 備考
}

# land_infoテーブル用
LAND_INFO_MAPPING = {
    "field28": "land_area",  # 土地面積
    "field26": "land_category",  # 地目
    "field25": "use_district",  # 用途地域
    "field30": "city_planning",  # 都市計画
    "field27": "building_coverage_ratio",  # 建蔽率
    "field29": "floor_area_ratio",  # 容積率
    "field42": "land_rights",  # 土地の権利
    "field31": "terrain",  # 地勢
    "field32": "legal_restrictions",  # その他法令上の制限
    "field43": "land_law_permission",  # 国土法の許可
    "field13": "chiban",  # 地番
}

# building_infoテーブル用
BUILDING_INFO_MAPPING = {
    "m2": "building_area",  # 建物面積
    "field22": "building_structure",  # 建物構造
    "field21": "building_floors_above",  # 地上階
    "field20": "building_floors_below",  # 地下階
    "field2": "room_type",  # 間取り
    "field48": "floor_plan_notes",  # 間取り内訳
    "field45": "parking_availability",  # 駐車場の有無
    "field44": "parking_notes",  # 駐車場その他
}

# 接道情報（JSONBで保存）
ROAD_INFO_FIELDS = {
    "field37": "road_access",  # 接道状況
    "field38": "road1_type",  # 接道1種別
    "field39": "road1_direction",  # 接道1方角
    "field33": "road1_width",  # 接道1幅員
    "field34": "road1_frontage",  # 接道1間口
    "field40": "road2_type",  # 接道2種別
    "field41": "road2_direction",  # 接道2方角
    "field35": "road2_width",  # 接道2幅員
    "field36": "road2_frontage",  # 接道2間口
}


class ZohoMapper:
    """ZOHOデータをREA形式に変換するマッパー"""

    def map_record(self, zoho_record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        ZOHOレコードをREA形式に変換

        Returns:
            {
                "properties": {...},
                "land_info": {...},
                "building_info": {...}
            }
        """
        result = {
            "properties": {},
            "land_info": {},
            "building_info": {}
        }

        # ZOHOのIDを保存
        zoho_id = str(zoho_record.get("id", ""))
        result["properties"]["zoho_id"] = zoho_id
        result["properties"]["zoho_synced_at"] = datetime.now()
        result["properties"]["zoho_sync_status"] = "synced"

        # propertiesテーブル
        for zoho_field, rea_column in PROPERTIES_MAPPING.items():
            if zoho_field in zoho_record:
                value = self._transform_value(rea_column, zoho_record[zoho_field])
                if value is not None:
                    result["properties"][rea_column] = value

        # land_infoテーブル
        for zoho_field, rea_column in LAND_INFO_MAPPING.items():
            if zoho_field in zoho_record:
                value = self._transform_value(rea_column, zoho_record[zoho_field])
                if value is not None:
                    result["land_info"][rea_column] = value

        # 接道情報（JSONB）
        road_info = {}
        for zoho_field, key in ROAD_INFO_FIELDS.items():
            if zoho_field in zoho_record and zoho_record[zoho_field]:
                road_info[key] = zoho_record[zoho_field]
        if road_info:
            result["land_info"]["road_info"] = road_info

        # building_infoテーブル
        for zoho_field, rea_column in BUILDING_INFO_MAPPING.items():
            if zoho_field in zoho_record:
                value = self._transform_value(rea_column, zoho_record[zoho_field])
                if value is not None:
                    result["building_info"][rea_column] = value

        # 築年月の処理（field12=年、field11=月）
        year = zoho_record.get("field12")
        month = zoho_record.get("field11")
        if year:
            try:
                y = int(year)
                m = int(month) if month else 1
                result["building_info"]["construction_date"] = f"{y}-{m:02d}-01"
            except (ValueError, TypeError):
                pass

        return result

    def _transform_value(self, column: str, value: Any) -> Any:
        """フィールド固有の変換処理"""
        if value is None or value == "":
            return None

        # 価格（数値に変換）
        if column == "sale_price":
            try:
                if isinstance(value, str):
                    value = value.replace(",", "").replace("円", "").replace("¥", "")
                return int(float(value))
            except (ValueError, TypeError):
                return None

        # 面積（小数に変換）
        if column in ("land_area", "building_area"):
            try:
                if isinstance(value, str):
                    value = value.replace(",", "").replace("㎡", "").replace("m2", "")
                return float(value)
            except (ValueError, TypeError):
                return None

        # 建蔽率・容積率（%を数値に）
        if column in ("building_coverage_ratio", "floor_area_ratio"):
            try:
                if isinstance(value, str):
                    value = value.replace("%", "")
                return float(value)
            except (ValueError, TypeError):
                return None

        # 緯度経度
        if column in ("latitude", "longitude"):
            try:
                return float(value)
            except (ValueError, TypeError):
                return None

        # 階数
        if column in ("building_floors_above", "building_floors_below"):
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        return value


# シングルトンインスタンス
zoho_mapper = ZohoMapper()
