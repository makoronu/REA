"""
REA チラシ・マイソク生成 基底クラス

メタデータ駆動: テンプレート定義・フィールドマッピングはYAMLから読み込み
共通処理集約: フォーマット関数は shared/real_estate_utils.py を使用
"""

import os
import yaml
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path


class FlyerGenerator(ABC):
    """チラシ・マイソク生成の基底クラス"""

    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / 'config'
        self.templates_dir = Path(__file__).parent.parent / 'templates'
        self._output_settings: Optional[Dict] = None
        self._templates: Optional[Dict] = None
        self._field_mappings: Optional[Dict] = None

    @property
    def output_settings(self) -> Dict:
        """出力設定を遅延読み込み"""
        if self._output_settings is None:
            self._output_settings = self._load_yaml('output_settings.yaml')
        return self._output_settings

    @property
    def templates(self) -> Dict:
        """テンプレート定義を遅延読み込み"""
        if self._templates is None:
            self._templates = self._load_yaml('templates.yaml')
        return self._templates

    @property
    def field_mappings(self) -> Dict:
        """フィールドマッピングを遅延読み込み"""
        if self._field_mappings is None:
            self._field_mappings = self._load_yaml('field_mappings.yaml')
        return self._field_mappings

    def _load_yaml(self, filename: str) -> Dict:
        """YAML設定ファイルを読み込み"""
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get_template_config(self, template_type: str, template_name: str) -> Dict:
        """
        テンプレート設定を取得

        Args:
            template_type: 'maisoku' or 'chirashi'
            template_name: テンプレート名（例: 'land', 'detached', 'single'）

        Returns:
            テンプレート設定辞書
        """
        if template_type not in self.templates:
            raise ValueError(f"不明なテンプレートタイプ: {template_type}")

        if template_name not in self.templates[template_type]:
            raise ValueError(f"不明なテンプレート: {template_type}/{template_name}")

        return self.templates[template_type][template_name]

    def get_field_config(self, field_name: str) -> Dict:
        """
        フィールド設定を取得

        Args:
            field_name: フィールド名

        Returns:
            フィールド設定辞書
        """
        fields = self.field_mappings.get('fields', {})
        if field_name not in fields:
            raise ValueError(f"不明なフィールド: {field_name}")
        return fields[field_name]

    def format_field_value(self, field_name: str, value: Any, property_data: Dict) -> str:
        """
        フィールド値をフォーマット

        Args:
            field_name: フィールド名
            value: 元の値
            property_data: 物件データ全体（計算フィールド用）

        Returns:
            フォーマット済み文字列
        """
        # フォーマット関数をshared/real_estate_utils.pyから取得
        from shared.real_estate_utils import (
            format_price_man,
            format_price_display,
            format_price_per_tsubo,
            format_area_with_tsubo,
            format_area_tsubo_only,
            format_building_age,
            format_percentage,
            format_floor_display,
            calculate_yield,
        )

        format_functions = {
            'format_price_man': format_price_man,
            'format_price_display': format_price_display,
            'format_price_per_tsubo': lambda p, a: format_price_per_tsubo(
                property_data.get('sale_price'),
                property_data.get('land_area')
            ),
            'format_area_with_tsubo': format_area_with_tsubo,
            'format_area_tsubo_only': format_area_tsubo_only,
            'format_building_age': format_building_age,
            'format_percentage': format_percentage,
            'format_floor_display': format_floor_display,
        }

        field_config = self.get_field_config(field_name)
        format_func_name = field_config.get('format')

        if format_func_name is None:
            # フォーマットなし: そのまま返す
            return str(value) if value is not None else ''

        if format_func_name in format_functions:
            return format_functions[format_func_name](value)

        # マスターテーブル参照の場合
        master_tables = self.field_mappings.get('master_tables', {})
        if format_func_name in master_tables:
            return self._get_master_label(format_func_name, value)

        return str(value) if value is not None else ''

    def _get_master_label(self, master_name: str, value: Any) -> str:
        """
        マスターテーブルからラベルを取得

        Args:
            master_name: マスターテーブル設定名
            value: 検索キー

        Returns:
            ラベル文字列
        """
        # TODO: DBからマスターテーブルを参照
        # 現時点では値をそのまま返す
        return str(value) if value is not None else ''

    def extract_property_data(self, property_full: Dict) -> Dict:
        """
        物件データからフラットな辞書を作成

        Args:
            property_full: /properties/{id}/full のレスポンス

        Returns:
            フラット化された物件データ
        """
        result = {}

        # properties直下のフィールド
        for key, value in property_full.items():
            if key not in ['building_info', 'land_info', 'images']:
                result[key] = value

        # building_info
        building_info = property_full.get('building_info') or {}
        for key, value in building_info.items():
            if key not in ['id', 'property_id', 'created_at', 'updated_at']:
                result[key] = value

        # land_info
        land_info = property_full.get('land_info') or {}
        for key, value in land_info.items():
            if key not in ['id', 'property_id', 'created_at', 'updated_at']:
                # 重複カラムはproperties優先
                if key not in result or result[key] is None:
                    result[key] = value

        return result

    def get_images(self, property_full: Dict, max_images: int = 6) -> List[str]:
        """
        物件画像URLリストを取得

        Args:
            property_full: 物件データ
            max_images: 最大画像数

        Returns:
            画像URLのリスト
        """
        images = property_full.get('images') or []
        # display_orderでソート
        sorted_images = sorted(images, key=lambda x: x.get('display_order', 999))
        return [img.get('image_url') for img in sorted_images[:max_images] if img.get('image_url')]

    @abstractmethod
    def generate(self, property_data: Dict, template_name: str) -> str:
        """
        SVGを生成（サブクラスで実装）

        Args:
            property_data: 物件データ
            template_name: テンプレート名

        Returns:
            SVG文字列
        """
        pass

    @abstractmethod
    def get_template_type(self) -> str:
        """テンプレートタイプを返す（'maisoku' or 'chirashi'）"""
        pass
