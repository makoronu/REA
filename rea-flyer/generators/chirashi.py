"""
チラシ生成クラス
複数物件を1枚のチラシにレイアウト
"""

from typing import Any, Dict, List, Optional

from .base import BaseGenerator


class ChirashiGenerator(BaseGenerator):
    """チラシ生成クラス"""

    def __init__(self):
        """初期化"""
        super().__init__()
        self.chirashi_config = self.templates_config.get("chirashi", {})

    def _get_layout_config(self, layout: str) -> Dict[str, Any]:
        """
        レイアウト設定を取得

        Args:
            layout: レイアウト名（single, dual, grid）

        Returns:
            Dict: レイアウト設定
        """
        config = self.chirashi_config.get(layout)
        if config is None:
            config = self.chirashi_config.get("single", {})
        return config

    def generate(
        self,
        property_data: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """
        チラシを生成（単一物件）

        Args:
            property_data: 物件データ
            output_path: 出力先パス

        Returns:
            str: SVG文字列またはファイルパス
        """
        return self.generate_multi([property_data], layout="single", output_path=output_path)

    def generate_multi(
        self,
        properties: List[Dict[str, Any]],
        layout: str = "single",
        output_path: Optional[str] = None,
    ) -> str:
        """
        チラシを生成（複数物件対応）

        Args:
            properties: 物件データのリスト
            layout: レイアウト（single, dual, grid）
            output_path: 出力先パス

        Returns:
            str: SVG文字列またはファイルパス
        """
        layout_config = self._get_layout_config(layout)
        max_properties = layout_config.get("max_properties", 1)

        # 最大件数を超えた場合は切り捨て
        properties = properties[:max_properties]

        # テンプレート読み込み or 動的生成
        template_path = layout_config.get("template", f"chirashi/{layout}.svg")
        try:
            svg_content = self._load_template(template_path)
            # 複数物件の場合はプレースホルダーを順番に置換
            for i, prop in enumerate(properties):
                svg_content = self._replace_indexed_placeholders(svg_content, prop, i)
        except FileNotFoundError:
            svg_content = self._generate_dynamic_chirashi(properties, layout_config)

        if output_path:
            return self._save_svg(svg_content, output_path)
        return svg_content

    def _replace_indexed_placeholders(
        self, svg_content: str, property_data: Dict[str, Any], index: int
    ) -> str:
        """
        インデックス付きプレースホルダーを置換

        例: {{property_name_0}}, {{price_1}}

        Args:
            svg_content: SVGテンプレート
            property_data: 物件データ
            index: 物件インデックス

        Returns:
            str: 置換後SVG
        """
        import re

        pattern = rf"\{{\{{(\w+)_{index}\}}\}}"

        def replacer(match):
            field_name = match.group(1)
            return self._get_field_value(property_data, field_name)

        return re.sub(pattern, replacer, svg_content)

    def _generate_dynamic_chirashi(
        self, properties: List[Dict[str, Any]], layout_config: Dict[str, Any]
    ) -> str:
        """
        動的チラシ生成

        Args:
            properties: 物件データリスト
            layout_config: レイアウト設定

        Returns:
            str: SVG文字列
        """
        paper_size = layout_config.get("paper_size", "a4")
        paper_config = self.output_settings.get("paper_sizes", {}).get(paper_size, {})
        width_mm = paper_config.get("width_mm", 210)
        height_mm = paper_config.get("height_mm", 297)
        bleed_mm = self.output_settings.get("output", {}).get("bleed_mm", 3)

        mm_to_px = self.output_settings.get("mm_to_px_ratio", 13.78)
        width_px = (width_mm + bleed_mm * 2) * mm_to_px
        height_px = (height_mm + bleed_mm * 2) * mm_to_px

        layout_type = layout_config.get("layout", "full_page")
        num_properties = len(properties)

        svg_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width_px:.0f}" height="{height_px:.0f}" '
            f'viewBox="0 0 {width_px:.0f} {height_px:.0f}">',
            '  <style>',
            '    .chirashi-title { font-family: "Noto Sans JP", sans-serif; font-size: 36px; font-weight: bold; fill: #1a1a1a; }',
            '    .chirashi-price { font-family: "Noto Sans JP", sans-serif; font-size: 48px; font-weight: bold; fill: #c41e3a; }',
            '    .chirashi-address { font-family: "Noto Sans JP", sans-serif; font-size: 20px; fill: #333; }',
            '    .chirashi-info { font-family: "Noto Sans JP", sans-serif; font-size: 16px; fill: #666; }',
            '    .chirashi-label { font-family: "Noto Sans JP", sans-serif; font-size: 14px; fill: #888; }',
            '  </style>',
            '  <rect width="100%" height="100%" fill="#ffffff"/>',
        ]

        # レイアウトに応じて物件を配置
        if layout_type == "full_page" and num_properties == 1:
            svg_parts.extend(self._render_single_property(properties[0], width_px, height_px))
        elif layout_type == "split_horizontal" and num_properties <= 2:
            svg_parts.extend(self._render_dual_properties(properties, width_px, height_px))
        elif layout_type == "grid_2x2" and num_properties <= 4:
            svg_parts.extend(self._render_grid_properties(properties, width_px, height_px))
        else:
            svg_parts.extend(self._render_single_property(properties[0], width_px, height_px))

        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

    def _render_single_property(
        self, prop: Dict[str, Any], width: float, height: float
    ) -> List[str]:
        """単一物件レンダリング"""
        parts = []
        margin = 80

        # 物件名
        name = self._get_field_value(prop, "property_name") or "物件名未定"
        parts.append(f'  <text x="{margin}" y="100" class="chirashi-title">{name}</text>')

        # 価格
        price = self._get_field_value(prop, "price") or "価格未定"
        parts.append(f'  <text x="{margin}" y="180" class="chirashi-price">{price}</text>')

        # 写真エリア
        photo_width = width - margin * 2
        photo_height = height * 0.4
        parts.append(
            f'  <rect x="{margin}" y="220" width="{photo_width}" height="{photo_height}" '
            f'fill="#f9fafb" stroke="#e5e7eb" rx="8"/>'
        )
        parts.append(
            f'  <text x="{width/2}" y="{220 + photo_height/2}" '
            f'class="chirashi-label" text-anchor="middle">メイン写真</text>'
        )

        # 住所
        address = self._get_field_value(prop, "address") or "住所未定"
        y_pos = 220 + photo_height + 60
        parts.append(f'  <text x="{margin}" y="{y_pos}" class="chirashi-address">{address}</text>')

        # 物件情報
        info_y = y_pos + 50
        land_area = self._get_field_value(prop, "land_area")
        building_area = self._get_field_value(prop, "building_area")

        if land_area:
            parts.append(f'  <text x="{margin}" y="{info_y}" class="chirashi-info">土地面積: {land_area}</text>')
            info_y += 30
        if building_area:
            parts.append(f'  <text x="{margin}" y="{info_y}" class="chirashi-info">建物面積: {building_area}</text>')

        return parts

    def _render_dual_properties(
        self, properties: List[Dict[str, Any]], width: float, height: float
    ) -> List[str]:
        """2物件レンダリング（上下分割）"""
        parts = []
        margin = 60
        half_height = height / 2

        for i, prop in enumerate(properties[:2]):
            y_offset = i * half_height
            name = self._get_field_value(prop, "property_name") or "物件名未定"
            price = self._get_field_value(prop, "price") or "価格未定"
            address = self._get_field_value(prop, "address") or "住所未定"

            parts.append(f'  <text x="{margin}" y="{y_offset + 60}" class="chirashi-title">{name}</text>')
            parts.append(f'  <text x="{margin}" y="{y_offset + 120}" class="chirashi-price">{price}</text>')

            # 写真エリア
            photo_width = (width - margin * 3) / 2
            photo_height = half_height * 0.5
            parts.append(
                f'  <rect x="{margin}" y="{y_offset + 150}" width="{photo_width}" height="{photo_height}" '
                f'fill="#f9fafb" stroke="#e5e7eb" rx="8"/>'
            )

            parts.append(f'  <text x="{margin}" y="{y_offset + 150 + photo_height + 30}" class="chirashi-address">{address}</text>')

            # 区切り線
            if i == 0:
                parts.append(f'  <line x1="0" y1="{half_height}" x2="{width}" y2="{half_height}" stroke="#e5e7eb" stroke-width="2"/>')

        return parts

    def _render_grid_properties(
        self, properties: List[Dict[str, Any]], width: float, height: float
    ) -> List[str]:
        """4物件レンダリング（2x2グリッド）"""
        parts = []
        margin = 40
        cell_width = width / 2
        cell_height = height / 2

        positions = [(0, 0), (1, 0), (0, 1), (1, 1)]

        for i, prop in enumerate(properties[:4]):
            col, row = positions[i]
            x_offset = col * cell_width + margin
            y_offset = row * cell_height + margin

            name = self._get_field_value(prop, "property_name") or "物件名未定"
            price = self._get_field_value(prop, "price") or "価格未定"
            address = self._get_field_value(prop, "address") or "住所未定"

            # 物件名（短縮）
            if len(name) > 15:
                name = name[:15] + "..."
            parts.append(f'  <text x="{x_offset}" y="{y_offset + 30}" class="chirashi-info" font-weight="bold">{name}</text>')

            # 価格
            parts.append(f'  <text x="{x_offset}" y="{y_offset + 70}" class="chirashi-price" style="font-size: 32px;">{price}</text>')

            # 写真エリア
            photo_width = cell_width - margin * 2
            photo_height = cell_height * 0.45
            parts.append(
                f'  <rect x="{x_offset}" y="{y_offset + 90}" width="{photo_width}" height="{photo_height}" '
                f'fill="#f9fafb" stroke="#e5e7eb" rx="4"/>'
            )

            # 住所（短縮）
            if len(address) > 20:
                address = address[:20] + "..."
            parts.append(f'  <text x="{x_offset}" y="{y_offset + 90 + photo_height + 25}" class="chirashi-label">{address}</text>')

        # グリッド線
        parts.append(f'  <line x1="{width/2}" y1="0" x2="{width/2}" y2="{height}" stroke="#e5e7eb" stroke-width="1"/>')
        parts.append(f'  <line x1="0" y1="{height/2}" x2="{width}" y2="{height/2}" stroke="#e5e7eb" stroke-width="1"/>')

        return parts
