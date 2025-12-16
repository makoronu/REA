"""
REA SVGビルダー

印刷入稿可能なSVGを生成するユーティリティ
プレースホルダー置換方式ではなく、動的にSVG要素を構築
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass
import xml.etree.ElementTree as ET


@dataclass
class SVGStyle:
    """SVGスタイル定義"""
    font_family: str = "Noto Sans JP"
    font_weight: str = "normal"
    fill: str = "#000000"
    stroke: Optional[str] = None
    stroke_width: float = 0


class SVGBuilder:
    """
    SVG文書を構築するビルダークラス

    印刷用SVG生成を考慮:
    - mm単位での座標指定
    - 塗り足し（bleed）対応
    - CMYKカラー（将来対応）
    """

    def __init__(
        self,
        width_mm: float = 210,
        height_mm: float = 297,
        bleed_mm: float = 3,
        viewbox_scale: float = 1.0
    ):
        """
        SVGビルダーを初期化

        Args:
            width_mm: 幅（mm）
            height_mm: 高さ（mm）
            bleed_mm: 塗り足し（mm）
            viewbox_scale: viewBoxスケール
        """
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.bleed_mm = bleed_mm
        self.viewbox_scale = viewbox_scale

        # 塗り足し込みのサイズ
        self.total_width = width_mm + (bleed_mm * 2)
        self.total_height = height_mm + (bleed_mm * 2)

        # SVG要素リスト
        self._elements: List[ET.Element] = []

        # デフォルトスタイル
        self._default_style = SVGStyle()

    def add_text(
        self,
        text: str,
        x: float,
        y: float,
        font_size: float = 3.5,
        font_weight: str = "normal",
        fill: str = "#000000",
        anchor: str = "start",
        max_width: Optional[float] = None
    ) -> 'SVGBuilder':
        """
        テキスト要素を追加

        Args:
            text: テキスト内容
            x: X座標（mm、塗り足し起点）
            y: Y座標（mm、塗り足し起点）
            font_size: フォントサイズ（mm）
            font_weight: フォントウェイト
            fill: 塗りつぶし色
            anchor: テキストアンカー（start, middle, end）
            max_width: 最大幅（mm、超えると省略）

        Returns:
            self（メソッドチェーン用）
        """
        # 塗り足し分をオフセット
        actual_x = x + self.bleed_mm
        actual_y = y + self.bleed_mm

        # テキストが長すぎる場合は省略
        if max_width and len(text) > 0:
            # 1文字あたりの概算幅（日本語）
            char_width = font_size * 0.9
            max_chars = int(max_width / char_width)
            if len(text) > max_chars:
                text = text[:max_chars - 1] + "…"

        elem = ET.Element('text')
        elem.set('x', f"{actual_x}mm")
        elem.set('y', f"{actual_y}mm")
        elem.set('font-size', f"{font_size}mm")
        elem.set('font-family', self._default_style.font_family)
        elem.set('font-weight', font_weight)
        elem.set('fill', fill)
        elem.set('text-anchor', anchor)
        elem.text = text

        self._elements.append(elem)
        return self

    def add_rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        fill: str = "#FFFFFF",
        stroke: Optional[str] = None,
        stroke_width: float = 0.5,
        rx: float = 0
    ) -> 'SVGBuilder':
        """
        矩形を追加

        Args:
            x: X座標（mm）
            y: Y座標（mm）
            width: 幅（mm）
            height: 高さ（mm）
            fill: 塗りつぶし色
            stroke: 枠線色
            stroke_width: 枠線幅（mm）
            rx: 角丸半径（mm）

        Returns:
            self
        """
        actual_x = x + self.bleed_mm
        actual_y = y + self.bleed_mm

        elem = ET.Element('rect')
        elem.set('x', f"{actual_x}mm")
        elem.set('y', f"{actual_y}mm")
        elem.set('width', f"{width}mm")
        elem.set('height', f"{height}mm")
        elem.set('fill', fill)

        if stroke:
            elem.set('stroke', stroke)
            elem.set('stroke-width', f"{stroke_width}mm")

        if rx > 0:
            elem.set('rx', f"{rx}mm")

        self._elements.append(elem)
        return self

    def add_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        stroke: str = "#000000",
        stroke_width: float = 0.3
    ) -> 'SVGBuilder':
        """
        線を追加

        Args:
            x1, y1: 始点座標（mm）
            x2, y2: 終点座標（mm）
            stroke: 線色
            stroke_width: 線幅（mm）

        Returns:
            self
        """
        elem = ET.Element('line')
        elem.set('x1', f"{x1 + self.bleed_mm}mm")
        elem.set('y1', f"{y1 + self.bleed_mm}mm")
        elem.set('x2', f"{x2 + self.bleed_mm}mm")
        elem.set('y2', f"{y2 + self.bleed_mm}mm")
        elem.set('stroke', stroke)
        elem.set('stroke-width', f"{stroke_width}mm")

        self._elements.append(elem)
        return self

    def add_image(
        self,
        href: str,
        x: float,
        y: float,
        width: float,
        height: float,
        preserve_aspect: bool = True
    ) -> 'SVGBuilder':
        """
        画像を追加

        Args:
            href: 画像URL
            x: X座標（mm）
            y: Y座標（mm）
            width: 幅（mm）
            height: 高さ（mm）
            preserve_aspect: アスペクト比を維持するか

        Returns:
            self
        """
        actual_x = x + self.bleed_mm
        actual_y = y + self.bleed_mm

        elem = ET.Element('image')
        elem.set('href', href)
        elem.set('x', f"{actual_x}mm")
        elem.set('y', f"{actual_y}mm")
        elem.set('width', f"{width}mm")
        elem.set('height', f"{height}mm")

        if preserve_aspect:
            elem.set('preserveAspectRatio', 'xMidYMid slice')
        else:
            elem.set('preserveAspectRatio', 'none')

        self._elements.append(elem)
        return self

    def add_group(self, id: str = None, transform: str = None) -> ET.Element:
        """
        グループ要素を追加

        Args:
            id: グループID
            transform: 変換（translate, rotate等）

        Returns:
            グループ要素（子要素を追加可能）
        """
        elem = ET.Element('g')
        if id:
            elem.set('id', id)
        if transform:
            elem.set('transform', transform)

        self._elements.append(elem)
        return elem

    def add_bleed_marks(self) -> 'SVGBuilder':
        """
        トンボ（トリムマーク）を追加

        Returns:
            self
        """
        mark_length = 5  # mm
        mark_offset = 1  # mm

        # 四隅にトンボを描画
        corners = [
            (0, 0, 'top-left'),
            (self.width_mm, 0, 'top-right'),
            (0, self.height_mm, 'bottom-left'),
            (self.width_mm, self.height_mm, 'bottom-right'),
        ]

        for x, y, pos in corners:
            if 'left' in pos:
                # 左側の横線
                self.add_line(x - mark_length - mark_offset, y, x - mark_offset, y, stroke='#000000', stroke_width=0.1)
            else:
                # 右側の横線
                self.add_line(x + mark_offset, y, x + mark_length + mark_offset, y, stroke='#000000', stroke_width=0.1)

            if 'top' in pos:
                # 上側の縦線
                self.add_line(x, y - mark_length - mark_offset, x, y - mark_offset, stroke='#000000', stroke_width=0.1)
            else:
                # 下側の縦線
                self.add_line(x, y + mark_offset, x, y + mark_length + mark_offset, stroke='#000000', stroke_width=0.1)

        return self

    def to_svg(self) -> str:
        """
        SVG文字列を生成

        Returns:
            SVG文字列
        """
        # SVGルート要素
        svg = ET.Element('svg')
        svg.set('xmlns', 'http://www.w3.org/2000/svg')
        svg.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
        svg.set('width', f"{self.total_width}mm")
        svg.set('height', f"{self.total_height}mm")
        svg.set('viewBox', f"0 0 {self.total_width} {self.total_height}")

        # スタイル定義
        style = ET.SubElement(svg, 'style')
        style.text = f"""
            text {{
                font-family: "{self._default_style.font_family}", sans-serif;
            }}
        """

        # 背景（塗り足し領域含む）
        bg = ET.SubElement(svg, 'rect')
        bg.set('x', '0')
        bg.set('y', '0')
        bg.set('width', f"{self.total_width}mm")
        bg.set('height', f"{self.total_height}mm")
        bg.set('fill', '#FFFFFF')

        # 要素を追加
        for elem in self._elements:
            svg.append(elem)

        # XML宣言付きで出力
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(svg, encoding='unicode')

    def to_file(self, filepath: str) -> None:
        """
        SVGファイルとして保存

        Args:
            filepath: 出力ファイルパス
        """
        svg_content = self.to_svg()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
