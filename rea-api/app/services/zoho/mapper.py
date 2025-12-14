"""
ZOHO CRM データマッピング

ZOHOのフィールド名 → REAのカラム名への変換を行う。
フィールド名はZOHO側の設定に依存するため、環境変数またはDBで設定可能。
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import os


# デフォルトのフィールドマッピング
# ZOHO側のフィールド名（API名）→ REA側のカラム名
DEFAULT_FIELD_MAPPING = {
    # 基本情報
    "Name": "property_name",
    "物件名": "property_name",
    "Property_Name": "property_name",

    # 価格
    "Price": "sale_price",
    "価格": "sale_price",
    "販売価格": "sale_price",
    "Sale_Price": "sale_price",

    # 住所
    "Address": "address",
    "住所": "address",
    "所在地": "address",

    # 都道府県
    "Prefecture": "prefecture",
    "都道府県": "prefecture",

    # 市区町村
    "City": "city",
    "市区町村": "city",

    # 町名・番地
    "Town": "town",
    "町名": "town",
    "番地": "chome_banchi",

    # 物件種別
    "Property_Type": "property_type",
    "物件種別": "property_type",

    # 土地面積
    "Land_Area": "land_area",
    "土地面積": "land_area",

    # 建物面積
    "Building_Area": "building_area",
    "建物面積": "building_area",
    "延床面積": "building_area",

    # 築年月
    "Built_Year": "construction_date",
    "築年月": "construction_date",
    "建築年月": "construction_date",

    # 間取り
    "Floor_Plan": "floor_plan",
    "間取り": "floor_plan",

    # 構造
    "Structure": "building_structure",
    "建物構造": "building_structure",

    # 備考
    "Remarks": "remarks",
    "備考": "remarks",
    "Description": "remarks",

    # ステータス
    "Status": "status",
    "ステータス": "status",
}


# 物件種別の変換マッピング
PROPERTY_TYPE_MAPPING = {
    "一戸建て": "detached_house",
    "マンション": "apartment",
    "アパート": "apartment_building",
    "土地": "land",
    "店舗": "store",
    "事務所": "office",
    "倉庫": "warehouse",
    "工場": "factory",
    "ビル": "building",
    "駐車場": "parking",
}


class ZohoMapper:
    """ZOHOデータをREA形式に変換するマッパー"""

    def __init__(self, custom_mapping: Optional[Dict[str, str]] = None):
        """
        Args:
            custom_mapping: カスタムフィールドマッピング（デフォルトをオーバーライド）
        """
        self.field_mapping = {**DEFAULT_FIELD_MAPPING}
        if custom_mapping:
            self.field_mapping.update(custom_mapping)

    def map_record(self, zoho_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        ZOHOレコードをREA形式に変換

        Args:
            zoho_record: ZOHOから取得したレコード

        Returns:
            REAのpropertiesテーブル形式のデータ
        """
        rea_data = {}

        # ZOHOのIDを保存
        rea_data["zoho_id"] = str(zoho_record.get("id", ""))
        rea_data["zoho_synced_at"] = datetime.now()
        rea_data["zoho_sync_status"] = "synced"

        # フィールドマッピングに従って変換
        for zoho_field, rea_column in self.field_mapping.items():
            if zoho_field in zoho_record:
                value = zoho_record[zoho_field]
                # 特殊な変換が必要なフィールド
                value = self._transform_value(rea_column, value)
                if value is not None:
                    rea_data[rea_column] = value

        # 追加の処理
        rea_data = self._post_process(rea_data, zoho_record)

        return rea_data

    def _transform_value(self, column: str, value: Any) -> Any:
        """フィールド固有の変換処理"""
        if value is None:
            return None

        # 物件種別の変換
        if column == "property_type":
            return PROPERTY_TYPE_MAPPING.get(str(value), str(value))

        # 価格（数値に変換）
        if column == "sale_price":
            try:
                if isinstance(value, str):
                    # カンマや円記号を除去
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

        # 日付
        if column == "construction_date":
            return self._parse_date(value)

        return value

    def _parse_date(self, value: Any) -> Optional[str]:
        """日付文字列をパース"""
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        # 文字列の場合、いくつかのフォーマットを試す
        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y年%m月%d日",
            "%Y年%m月",
            "%Y-%m",
            "%Y/%m",
        ]

        value_str = str(value)
        for fmt in date_formats:
            try:
                dt = datetime.strptime(value_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return None

    def _post_process(self, rea_data: Dict[str, Any], zoho_record: Dict[str, Any]) -> Dict[str, Any]:
        """変換後の追加処理"""
        # 住所から都道府県・市区町村を分離（住所があるが都道府県がない場合）
        if rea_data.get("address") and not rea_data.get("prefecture"):
            prefecture, city, town = self._parse_address(rea_data["address"])
            if prefecture:
                rea_data.setdefault("prefecture", prefecture)
            if city:
                rea_data.setdefault("city", city)
            if town:
                rea_data.setdefault("town", town)

        # ステータスのデフォルト値
        if not rea_data.get("status"):
            rea_data["status"] = "査定中"

        return rea_data

    def _parse_address(self, address: str) -> tuple:
        """住所を都道府県・市区町村・町名に分離"""
        # 都道府県リスト
        prefectures = [
            "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
            "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
            "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
            "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
            "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
            "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
            "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
        ]

        prefecture = None
        city = None
        town = None
        remaining = address

        # 都道府県を抽出
        for pref in prefectures:
            if address.startswith(pref):
                prefecture = pref
                remaining = address[len(pref):]
                break

        # 市区町村を抽出（簡易版：〜市、〜区、〜町、〜村で分割）
        import re
        city_match = re.match(r'^(.+?[市区町村])', remaining)
        if city_match:
            city = city_match.group(1)
            town = remaining[len(city):]
        else:
            town = remaining

        return prefecture, city, town

    def get_unmapped_fields(self, zoho_record: Dict[str, Any]) -> List[str]:
        """マッピングされていないフィールドを取得"""
        mapped_fields = set(self.field_mapping.keys())
        record_fields = set(zoho_record.keys())
        # システムフィールドを除外
        system_fields = {"id", "Created_Time", "Modified_Time", "Created_By", "Modified_By", "$"}
        unmapped = record_fields - mapped_fields - system_fields
        return [f for f in unmapped if not f.startswith("$")]


# シングルトンインスタンス
zoho_mapper = ZohoMapper()
