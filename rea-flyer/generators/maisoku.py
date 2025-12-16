"""
REA マイソク生成

メタデータ駆動でSVGテンプレートを埋める
"""

import sys
from pathlib import Path
from typing import Dict, Any

# パッケージルートをパスに追加
_pkg_root = Path(__file__).parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from generators.base import FlyerGenerator
from utils.svg_builder import SVGBuilder


class MaisokuGenerator(FlyerGenerator):
    """マイソク生成クラス"""

    def get_template_type(self) -> str:
        return 'maisoku'

    def select_template(self, property_type: str) -> str:
        """
        物件種別からテンプレートを自動選択

        Args:
            property_type: 物件種別ID

        Returns:
            テンプレート名
        """
        # 物件種別→テンプレートのマッピング
        type_to_template = {
            'land': 'land',
            'detached': 'detached',
            'house': 'detached',
            'apartment': 'apartment',
            'mansion': 'apartment',
            'investment': 'investment',
            'rental': 'investment',
        }
        return type_to_template.get(property_type, 'detached')

    def generate(self, property_data: Dict, template_name: str = None) -> str:
        """
        マイソクSVGを生成

        Args:
            property_data: 物件データ（/properties/{id}/fullのレスポンス）
            template_name: テンプレート名（省略時は自動選択）

        Returns:
            SVG文字列
        """
        # テンプレート自動選択
        if template_name is None:
            property_type = property_data.get('property_type', 'detached')
            template_name = self.select_template(property_type)

        # テンプレート設定取得
        template_config = self.get_template_config('maisoku', template_name)

        # 物件データをフラット化
        flat_data = self.extract_property_data(property_data)

        # 出力設定取得
        paper_size_name = template_config.get('paper_size', 'a4')
        paper_size = self.output_settings['paper_sizes'][paper_size_name]

        # SVGビルダー作成
        builder = SVGBuilder(
            width_mm=paper_size['width_mm'],
            height_mm=paper_size['height_mm'],
            bleed_mm=self.output_settings['output']['bleed_mm']
        )

        # セクションごとに生成
        for section in template_config.get('sections', []):
            section_name = section['name']

            if section_name == 'header':
                self._render_header(builder, section, flat_data)
            elif section_name == 'location':
                self._render_location(builder, section, flat_data)
            elif section_name == 'land_info':
                self._render_land_info(builder, section, flat_data)
            elif section_name == 'building_info':
                self._render_building_info(builder, section, flat_data)
            elif section_name == 'transaction':
                self._render_transaction(builder, section, flat_data)
            elif section_name == 'photos':
                images = self.get_images(property_data, section.get('max_images', 6))
                self._render_photos(builder, images)
            elif section_name == 'company':
                self._render_company(builder, section, flat_data)
            elif section_name == 'management':
                self._render_management(builder, section, flat_data)
            elif section_name == 'income':
                self._render_income(builder, section, flat_data)

        return builder.to_svg()

    def _render_header(self, builder: SVGBuilder, section: Dict, data: Dict) -> None:
        """ヘッダーセクション描画"""
        fields = section.get('fields', [])
        y = 20  # mm

        for field_name in fields:
            value = data.get(field_name.replace('_', ''))  # カラム名調整
            # 実際のDB列名を探す
            for key in data.keys():
                if field_name in key or key in field_name:
                    value = data[key]
                    break

            formatted = self.format_field_value(field_name, value, data)
            if formatted:
                builder.add_text(
                    text=formatted,
                    x=10,
                    y=y,
                    font_size=self.output_settings['fonts']['title'] if field_name == 'property_name' else self.output_settings['fonts']['heading']
                )
                y += 10

    def _render_location(self, builder: SVGBuilder, section: Dict, data: Dict) -> None:
        """所在地セクション描画"""
        # TODO: 実装
        pass

    def _render_land_info(self, builder: SVGBuilder, section: Dict, data: Dict) -> None:
        """土地情報セクション描画"""
        # TODO: 実装
        pass

    def _render_building_info(self, builder: SVGBuilder, section: Dict, data: Dict) -> None:
        """建物情報セクション描画"""
        # TODO: 実装
        pass

    def _render_transaction(self, builder: SVGBuilder, section: Dict, data: Dict) -> None:
        """取引情報セクション描画"""
        # TODO: 実装
        pass

    def _render_photos(self, builder: SVGBuilder, images: list) -> None:
        """写真セクション描画"""
        # TODO: 実装
        pass

    def _render_company(self, builder: SVGBuilder, section: Dict, data: Dict) -> None:
        """会社情報セクション描画"""
        # TODO: 実装
        pass

    def _render_management(self, builder: SVGBuilder, section: Dict, data: Dict) -> None:
        """管理情報セクション描画（マンション用）"""
        # TODO: 実装
        pass

    def _render_income(self, builder: SVGBuilder, section: Dict, data: Dict) -> None:
        """収益情報セクション描画（収益物件用）"""
        # TODO: 実装
        pass
