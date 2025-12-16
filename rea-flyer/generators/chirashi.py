"""
REA チラシ生成

メタデータ駆動でSVGテンプレートを埋める
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# パッケージルートをパスに追加
_pkg_root = Path(__file__).parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from generators.base import FlyerGenerator
from utils.svg_builder import SVGBuilder


class ChirashiGenerator(FlyerGenerator):
    """チラシ生成クラス"""

    def get_template_type(self) -> str:
        return 'chirashi'

    def generate(self, property_data: Dict, template_name: str = 'single') -> str:
        """
        チラシSVGを生成（1件用）

        Args:
            property_data: 物件データ（/properties/{id}/fullのレスポンス）
            template_name: テンプレート名

        Returns:
            SVG文字列
        """
        return self.generate_multi([property_data], template_name)

    def generate_multi(self, properties: List[Dict], template_name: str = 'single') -> str:
        """
        チラシSVGを生成（複数件対応）

        Args:
            properties: 物件データのリスト
            template_name: テンプレート名（'single', 'dual', 'grid'）

        Returns:
            SVG文字列
        """
        # テンプレート設定取得
        template_config = self.get_template_config('chirashi', template_name)
        max_properties = template_config.get('max_properties', 1)

        # 物件数チェック
        if len(properties) > max_properties:
            properties = properties[:max_properties]

        # 出力設定取得
        paper_size_name = template_config.get('paper_size', 'a4')
        paper_size = self.output_settings['paper_sizes'][paper_size_name]

        # SVGビルダー作成
        builder = SVGBuilder(
            width_mm=paper_size['width_mm'],
            height_mm=paper_size['height_mm'],
            bleed_mm=self.output_settings['output']['bleed_mm']
        )

        # レイアウトに応じて描画
        layout = template_config.get('layout', 'full_page')

        if layout == 'full_page':
            self._render_single(builder, properties[0], template_config)
        elif layout == 'vertical_split':
            self._render_dual(builder, properties, template_config)
        elif layout == 'grid_2x2':
            self._render_grid(builder, properties, template_config)

        return builder.to_svg()

    def _render_single(self, builder: SVGBuilder, property_data: Dict, config: Dict) -> None:
        """1件用レイアウト描画"""
        flat_data = self.extract_property_data(property_data)
        images = self.get_images(property_data, 4)

        # メイン写真
        if images:
            builder.add_image(images[0], x=10, y=10, width=190, height=120)

        # サブ写真
        for i, img_url in enumerate(images[1:4]):
            builder.add_image(img_url, x=10 + i * 65, y=135, width=60, height=40)

        # 物件名・価格
        property_name = flat_data.get('property_name', '')
        builder.add_text(property_name, x=10, y=185, font_size=self.output_settings['fonts']['title'])

        price = flat_data.get('sale_price')
        formatted_price = self.format_field_value('price', price, flat_data)
        builder.add_text(formatted_price, x=10, y=195, font_size=self.output_settings['fonts']['heading'])

        # TODO: その他の情報描画

    def _render_dual(self, builder: SVGBuilder, properties: List[Dict], config: Dict) -> None:
        """2件用レイアウト描画（上下分割）"""
        # TODO: 実装
        pass

    def _render_grid(self, builder: SVGBuilder, properties: List[Dict], config: Dict) -> None:
        """4件用レイアウト描画（グリッド）"""
        # TODO: 実装
        pass
