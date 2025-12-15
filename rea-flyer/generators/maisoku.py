"""
マイソク生成クラス
物件種別に応じて適切なテンプレートを自動選択
"""

from typing import Any, Dict, Optional

from .base import BaseGenerator


class MaisokuGenerator(BaseGenerator):
    """マイソク生成クラス"""

    # 物件種別 → テンプレート名マッピング
    PROPERTY_TYPE_MAP = {
        "land": "land",           # 土地
        "detached": "detached",   # 戸建て
        "apartment": "apartment", # マンション
        "investment": "investment", # 収益物件
    }

    def __init__(self):
        """初期化"""
        super().__init__()
        self.maisoku_config = self.templates_config.get("maisoku", {})

    def _determine_template(self, property_type: str) -> str:
        """
        物件種別からテンプレート名を決定

        Args:
            property_type: 物件種別（DBのproperty_typeカラム値）

        Returns:
            str: テンプレート名
        """
        # DBの値をテンプレート名にマッピング
        template_name = self.PROPERTY_TYPE_MAP.get(property_type, "land")
        return template_name

    def _get_template_config(self, template_name: str) -> Dict[str, Any]:
        """
        テンプレート設定を取得

        Args:
            template_name: テンプレート名

        Returns:
            Dict: テンプレート設定
        """
        config = self.maisoku_config.get(template_name)
        if config is None:
            # デフォルトはland
            config = self.maisoku_config.get("land", {})
        return config

    # 利用可能なフォント一覧
    AVAILABLE_FONTS = {
        "Noto Sans JP": '"Noto Sans JP", sans-serif',
        "Hiragino Kaku Gothic": '"Hiragino Kaku Gothic ProN", "Hiragino Sans", sans-serif',
        "Meiryo": '"Meiryo", "メイリオ", sans-serif',
        "Yu Gothic": '"Yu Gothic", "游ゴシック", sans-serif',
    }

    def generate(
        self,
        property_data: Dict[str, Any],
        output_path: Optional[str] = None,
        font_family: str = "Noto Sans JP",
        font_scale: float = 1.0,
    ) -> str:
        """
        マイソクを生成

        Args:
            property_data: 物件データ（/properties/{id}/full APIレスポンス）
            output_path: 出力先パス（指定しない場合はSVG文字列を返す）
            font_family: フォント名
            font_scale: 文字サイズ倍率（0.8〜1.5）

        Returns:
            str: 生成されたSVG文字列、またはファイルパス
        """
        # 物件種別を取得
        property_type = property_data.get("property_type", "land")

        # テンプレートを決定
        template_name = self._determine_template(property_type)
        template_config = self._get_template_config(template_name)

        # テンプレートファイル読み込み
        template_path = template_config.get("template", f"maisoku/{template_name}.svg")
        try:
            svg_content = self._load_template(template_path)
        except FileNotFoundError:
            # テンプレートが存在しない場合は動的生成
            svg_content = self._generate_dynamic_svg(property_data, template_config)

        # フォント・サイズ適用
        svg_content = self._apply_font_settings(svg_content, font_family, font_scale)

        # プレースホルダー置換
        svg_result = self._replace_placeholders(svg_content, property_data)

        # 出力
        if output_path:
            return self._save_svg(svg_result, output_path)
        return svg_result

    def _apply_font_settings(
        self, svg_content: str, font_family: str, font_scale: float
    ) -> str:
        """
        SVGにフォント設定を適用

        Args:
            svg_content: SVG文字列
            font_family: フォント名
            font_scale: 文字サイズ倍率

        Returns:
            str: フォント設定適用後のSVG
        """
        import re

        # フォント名を取得
        font_stack = self.AVAILABLE_FONTS.get(font_family, self.AVAILABLE_FONTS["Noto Sans JP"])

        # font-familyを置換
        svg_content = re.sub(
            r'font-family:\s*"Noto Sans JP"[^;]*;',
            f'font-family: {font_stack};',
            svg_content
        )

        # font-sizeを倍率適用
        if font_scale != 1.0:
            def scale_font_size(match):
                size = float(match.group(1))
                new_size = size * font_scale
                return f'font-size: {new_size:.0f}px'

            svg_content = re.sub(
                r'font-size:\s*(\d+(?:\.\d+)?)px',
                scale_font_size,
                svg_content
            )

        return svg_content

    def _generate_dynamic_svg(
        self, property_data: Dict[str, Any], template_config: Dict[str, Any]
    ) -> str:
        """
        テンプレートが存在しない場合の動的SVG生成

        Args:
            property_data: 物件データ
            template_config: テンプレート設定

        Returns:
            str: 生成されたSVG文字列
        """
        # 出力設定を取得
        paper_size = template_config.get("paper_size", "a4")
        paper_config = self.output_settings.get("paper_sizes", {}).get(paper_size, {})
        width_mm = paper_config.get("width_mm", 210)
        height_mm = paper_config.get("height_mm", 297)
        bleed_mm = self.output_settings.get("output", {}).get("bleed_mm", 3)

        # mm → px変換
        mm_to_px = self.output_settings.get("mm_to_px_ratio", 13.78)
        width_px = (width_mm + bleed_mm * 2) * mm_to_px
        height_px = (height_mm + bleed_mm * 2) * mm_to_px

        # セクション取得
        sections = template_config.get("sections", [])

        # SVG生成
        svg_parts = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width_px:.0f}" height="{height_px:.0f}" '
            f'viewBox="0 0 {width_px:.0f} {height_px:.0f}">',
            f'  <style>',
            f'    .title {{ font-family: "Noto Sans JP", sans-serif; font-size: 24px; font-weight: bold; }}',
            f'    .label {{ font-family: "Noto Sans JP", sans-serif; font-size: 12px; fill: #666; }}',
            f'    .value {{ font-family: "Noto Sans JP", sans-serif; font-size: 14px; fill: #333; }}',
            f'    .price {{ font-family: "Noto Sans JP", sans-serif; font-size: 32px; font-weight: bold; fill: #c00; }}',
            f'  </style>',
            f'  <!-- 背景 -->',
            f'  <rect width="100%" height="100%" fill="white"/>',
        ]

        # セクションごとにコンテンツ生成
        y_offset = 60  # 開始位置
        for section in sections:
            section_name = section.get("name", "")
            fields = section.get("fields", [])

            # セクションタイトル
            svg_parts.append(
                f'  <text x="40" y="{y_offset}" class="title">{self._get_section_label(section_name)}</text>'
            )
            y_offset += 30

            # フィールド
            for field_name in fields:
                label = self._get_field_label(field_name)
                svg_parts.append(
                    f'  <text x="40" y="{y_offset}" class="label">{label}</text>'
                )
                # プレースホルダー
                css_class = "price" if field_name == "price" else "value"
                svg_parts.append(
                    f'  <text x="150" y="{y_offset}" class="{css_class}">{{{{{field_name}}}}}</text>'
                )
                y_offset += 25

            y_offset += 20  # セクション間スペース

        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

    def _get_section_label(self, section_name: str) -> str:
        """セクション名の日本語ラベルを取得"""
        labels = {
            "header": "物件概要",
            "location": "所在地",
            "land_info": "土地情報",
            "building_info": "建物情報",
            "transaction": "取引条件",
            "income": "収益情報",
        }
        return labels.get(section_name, section_name)

    def _get_field_label(self, field_name: str) -> str:
        """フィールド名の日本語ラベルを取得（column_labels連携）"""
        # 簡易マッピング（本番ではDBから取得）
        labels = {
            "property_name": "物件名",
            "price": "価格",
            "price_per_tsubo": "坪単価",
            "address": "所在地",
            "access": "交通",
            "land_area": "土地面積",
            "land_area_tsubo": "土地面積（坪）",
            "use_district": "用途地域",
            "building_coverage": "建ぺい率",
            "floor_area_ratio": "容積率",
            "building_area": "建物面積",
            "floor_plan": "間取り",
            "building_structure": "構造",
            "construction_date": "築年月",
            "floor": "所在階",
            "total_floors": "総階数",
            "transaction_type": "取引態様",
            "delivery_timing": "引渡し時期",
            "yield_rate": "表面利回り",
            "monthly_rent": "月額賃料",
            "annual_income": "年間収入",
        }
        return labels.get(field_name, field_name)
