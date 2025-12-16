"""
SVGビルダーのテスト
"""

import pytest
import sys
from pathlib import Path

# rea-flyerをパスに追加
rea_flyer_path = Path(__file__).parent.parent
sys.path.insert(0, str(rea_flyer_path))

from utils.svg_builder import SVGBuilder


class TestSVGBuilder:
    """SVGビルダーのテストケース"""

    def test_init_default(self):
        """デフォルト初期化テスト"""
        builder = SVGBuilder()
        assert builder.width_mm == 210
        assert builder.height_mm == 297
        assert builder.bleed_mm == 3
        assert builder.total_width == 216
        assert builder.total_height == 303

    def test_init_custom(self):
        """カスタム初期化テスト"""
        builder = SVGBuilder(width_mm=100, height_mm=150, bleed_mm=5)
        assert builder.width_mm == 100
        assert builder.height_mm == 150
        assert builder.total_width == 110
        assert builder.total_height == 160

    def test_add_text(self):
        """テキスト追加テスト"""
        builder = SVGBuilder()
        result = builder.add_text("テスト", x=10, y=20)
        assert result is builder  # メソッドチェーン
        assert len(builder._elements) == 1

    def test_add_rect(self):
        """矩形追加テスト"""
        builder = SVGBuilder()
        builder.add_rect(x=10, y=20, width=50, height=30)
        assert len(builder._elements) == 1

    def test_add_image(self):
        """画像追加テスト"""
        builder = SVGBuilder()
        builder.add_image("https://example.com/image.jpg", x=10, y=20, width=100, height=80)
        assert len(builder._elements) == 1

    def test_to_svg(self):
        """SVG出力テスト"""
        builder = SVGBuilder()
        builder.add_text("物件名", x=10, y=20, font_size=8)
        builder.add_rect(x=10, y=30, width=100, height=50, fill="#F0F0F0")

        svg = builder.to_svg()

        assert '<?xml version="1.0" encoding="UTF-8"?>' in svg
        assert '<svg' in svg
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg
        assert '物件名' in svg
        assert '</svg>' in svg

    def test_method_chaining(self):
        """メソッドチェーンテスト"""
        builder = SVGBuilder()
        result = (
            builder
            .add_text("テスト1", x=10, y=10)
            .add_text("テスト2", x=10, y=20)
            .add_rect(x=10, y=30, width=100, height=50)
        )
        assert result is builder
        assert len(builder._elements) == 3

    def test_bleed_offset(self):
        """塗り足しオフセットテスト"""
        builder = SVGBuilder(bleed_mm=5)
        builder.add_text("テスト", x=0, y=0)

        svg = builder.to_svg()
        # x=0は塗り足し5mm分オフセットされて5mmになる
        assert 'x="5mm"' in svg


class TestSVGBuilderOutput:
    """SVG出力品質テスト"""

    def test_svg_has_viewbox(self):
        """viewBoxが正しく設定されているか"""
        builder = SVGBuilder(width_mm=210, height_mm=297, bleed_mm=3)
        svg = builder.to_svg()
        assert 'viewBox="0 0 216 303"' in svg

    def test_svg_has_dimensions(self):
        """width/heightが正しく設定されているか"""
        builder = SVGBuilder(width_mm=210, height_mm=297, bleed_mm=3)
        svg = builder.to_svg()
        assert 'width="216mm"' in svg
        assert 'height="303mm"' in svg


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
