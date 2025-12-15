"""
チラシ・マイソク生成基底クラス
メタデータ駆動：YAML設定ファイルからテンプレート・フィールドマッピングを読み込む
"""

import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from shared.real_estate_utils import (
    format_area_tsubo_only,
    format_area_with_tsubo,
    format_building_age,
    format_floor_display,
    format_percentage,
    format_price_man,
    format_price_per_tsubo,
    format_wareki_year,
    to_float,
)


class BaseGenerator(ABC):
    """チラシ・マイソク生成基底クラス"""

    # 設定ファイルパス（クラス変数）
    CONFIG_DIR = Path(__file__).parent.parent / "config"
    TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

    # フォーマット関数マッピング（メタデータ駆動）
    FORMAT_FUNCTIONS = {
        "price_man": format_price_man,
        "area_with_tsubo": format_area_with_tsubo,
        "area_tsubo_only": format_area_tsubo_only,
        "building_age": format_building_age,
        "percentage": format_percentage,
        "floor_display": format_floor_display,
        "wareki_year": format_wareki_year,
        # 計算系は別途処理
    }

    def __init__(self):
        """初期化：設定ファイル読み込み"""
        self.output_settings = self._load_yaml("output_settings.yaml")
        self.templates_config = self._load_yaml("templates.yaml")
        self.field_mappings = self._load_yaml("field_mappings.yaml")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """YAML設定ファイル読み込み"""
        filepath = self.CONFIG_DIR / filename
        if not filepath.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_template(self, template_path: str) -> str:
        """SVGテンプレート読み込み"""
        filepath = self.TEMPLATES_DIR / template_path
        if not filepath.exists():
            raise FileNotFoundError(f"テンプレートが見つかりません: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _format_value(self, value: Any, format_type: Optional[str]) -> str:
        """
        値をフォーマット（メタデータ駆動）

        Args:
            value: フォーマット対象の値
            format_type: フォーマットタイプ（field_mappings.yamlで指定）

        Returns:
            str: フォーマット済み文字列
        """
        if value is None:
            return ""

        if format_type is None:
            return str(value)

        format_func = self.FORMAT_FUNCTIONS.get(format_type)
        if format_func:
            return format_func(value)

        # 未知のフォーマットタイプはそのまま返す
        return str(value)

    def _get_field_value(
        self, property_data: Dict[str, Any], field_name: str
    ) -> str:
        """
        フィールド値を取得してフォーマット

        Args:
            property_data: 物件データ（全テーブル結合済み）
            field_name: フィールド名（field_mappings.yamlのキー）

        Returns:
            str: フォーマット済みフィールド値
        """
        # 住所フィールドは特別処理（複数カラム結合）
        if field_name == "address":
            return self._build_full_address(property_data)

        field_config = self.field_mappings.get("fields", {}).get(field_name, {})

        # ソースカラム取得
        source = field_config.get("source")
        if source is None:
            # 計算フィールドの場合
            calculate = field_config.get("calculate")
            if calculate:
                return self._calculate_field(property_data, calculate, field_config)
            return ""

        # テーブル.カラム形式をパース
        if "." in source:
            table, column = source.split(".", 1)
            value = property_data.get(column)
        else:
            value = property_data.get(source)

        # フォーマット適用
        format_type = field_config.get("format")
        return self._format_value(value, format_type)

    def _build_full_address(self, property_data: Dict[str, Any]) -> str:
        """
        フル住所を組み立て

        Args:
            property_data: 物件データ

        Returns:
            str: 組み立てた住所文字列
        """
        parts = []
        for key in ["prefecture", "city", "address", "address_detail"]:
            value = property_data.get(key)
            if value:
                parts.append(str(value))
        return "".join(parts) if parts else "住所未定"

    def _calculate_field(
        self,
        property_data: Dict[str, Any],
        calculate: str,
        field_config: Dict[str, Any],
    ) -> str:
        """
        計算フィールドを処理

        Args:
            property_data: 物件データ
            calculate: 計算式（例: "sale_price / (land_area * 0.3025)"）
            field_config: フィールド設定

        Returns:
            str: 計算結果をフォーマットした文字列
        """
        # 坪単価の場合は専用関数を使用
        if "price_per_tsubo" in calculate.lower() or (
            "sale_price" in calculate and "land_area" in calculate
        ):
            price = property_data.get("sale_price")
            area = property_data.get("land_area")
            return format_price_per_tsubo(price, area)

        # 年間収入の場合
        if "monthly_rent" in calculate and "12" in calculate:
            monthly = to_float(property_data.get("monthly_rent"))
            if monthly:
                return format_price_man(monthly * 12)
            return "収入未定"

        return ""

    def _replace_placeholders(
        self, svg_content: str, property_data: Dict[str, Any]
    ) -> str:
        """
        SVGテンプレート内のプレースホルダーを置換

        Args:
            svg_content: SVGテンプレート文字列
            property_data: 物件データ

        Returns:
            str: プレースホルダー置換済みSVG
        """
        # {{field_name}} 形式のプレースホルダーを検索
        pattern = r"\{\{(\w+)\}\}"

        def replacer(match):
            field_name = match.group(1)
            return self._get_field_value(property_data, field_name)

        result = re.sub(pattern, replacer, svg_content)

        # 画像プレースホルダー置換（{{main_image}}）
        result = self._replace_image_placeholder(result, property_data)

        return result

    def _replace_image_placeholder(
        self, svg_content: str, property_data: Dict[str, Any]
    ) -> str:
        """
        画像プレースホルダーを置換（複数画像対応）

        Args:
            svg_content: SVG文字列
            property_data: 物件データ（_images, _main_imageキー含む）

        Returns:
            str: 画像置換済みSVG
        """
        # 複数画像対応（_imagesディクショナリ）
        images = property_data.get("_images", {})

        for image_key, image_data in images.items():
            if not image_data:
                continue

            # Base64画像がある場合
            if image_data.get("type") == "base64" and image_data.get("data"):
                # <image>タグのhref属性を置換
                placeholder = "{{" + image_key + "}}"
                svg_content = svg_content.replace(
                    f'href="{placeholder}"',
                    f'href="{image_data["data"]}"'
                )
                svg_content = svg_content.replace(
                    f'xlink:href="{placeholder}"',
                    f'xlink:href="{image_data["data"]}"'
                )

        # 後方互換性: _main_image単独の場合も処理
        if "_main_image" in property_data and "main_image" not in images:
            main_image = property_data["_main_image"]
            if main_image.get("type") == "base64" and main_image.get("data"):
                svg_content = svg_content.replace(
                    'href="{{main_image}}"',
                    f'href="{main_image["data"]}"'
                )
                svg_content = svg_content.replace(
                    'xlink:href="{{main_image}}"',
                    f'xlink:href="{main_image["data"]}"'
                )

        return svg_content

    @abstractmethod
    def generate(
        self, property_data: Dict[str, Any], output_path: Optional[str] = None
    ) -> str:
        """
        チラシ/マイソクを生成

        Args:
            property_data: 物件データ（APIから取得した全データ）
            output_path: 出力先パス（指定しない場合は文字列で返す）

        Returns:
            str: 生成されたSVG文字列、またはファイルパス
        """
        pass

    def _save_svg(self, svg_content: str, output_path: str) -> str:
        """SVGファイル保存"""
        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        return output_path
