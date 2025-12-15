"""
画像ハンドラ
チラシ・マイソク用の画像取得・変換処理
メタデータ駆動：設定はconfig/output_settings.yamlで管理
"""

import base64
import io
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import yaml

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import requests
except ImportError:
    requests = None


class ImageHandler:
    """
    画像ハンドラクラス
    property_imagesテーブルから画像を取得し、SVG埋め込み用に変換
    """

    # 設定ファイルパス
    CONFIG_PATH = Path(__file__).parent.parent / "config" / "output_settings.yaml"

    # デフォルト設定（設定ファイルがない場合のフォールバック）
    DEFAULT_CONFIG = {
        "image": {
            "max_width_px": 800,
            "max_height_px": 600,
            "quality": 85,
            "format": "JPEG",
            "placeholder_color": "#f3f4f6",
            "placeholder_text": "写真なし",
        }
    }

    def __init__(self):
        """初期化：設定ファイル読み込み"""
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        if self.CONFIG_PATH.exists():
            with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get("image", self.DEFAULT_CONFIG["image"])
        return self.DEFAULT_CONFIG["image"]

    def get_property_images(
        self, property_id: int, db_connection
    ) -> List[Dict[str, Any]]:
        """
        物件の画像一覧を取得

        Args:
            property_id: 物件ID
            db_connection: DB接続

        Returns:
            list: 画像情報リスト（display_order順）
        """
        cur = db_connection.cursor()
        try:
            cur.execute(
                """
                SELECT id, file_path, file_url, image_type, display_order, caption, is_public
                FROM property_images
                WHERE property_id = %s
                ORDER BY display_order ASC, id ASC
                """,
                (property_id,),
            )
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cur.close()

    def get_main_image(
        self, property_id: int, db_connection
    ) -> Optional[Dict[str, Any]]:
        """
        メイン画像（display_order=1 or 最小）を取得

        Args:
            property_id: 物件ID
            db_connection: DB接続

        Returns:
            dict: 画像情報、またはNone
        """
        images = self.get_property_images(property_id, db_connection)
        if images:
            return images[0]
        return None

    def image_to_base64(
        self, image_path: Optional[str] = None, image_url: Optional[str] = None
    ) -> Optional[str]:
        """
        画像をBase64エンコード

        Args:
            image_path: ローカルファイルパス
            image_url: リモートURL

        Returns:
            str: Base64エンコード済み文字列（data URI形式）
        """
        if Image is None:
            return None

        image_data = None

        # ローカルファイル
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                image_data = f.read()

        # リモートURL
        elif image_url and requests:
            try:
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    image_data = response.content
            except Exception:
                pass

        if not image_data:
            return None

        # 画像リサイズ・最適化
        try:
            img = Image.open(io.BytesIO(image_data))

            # RGBモード変換（CMYK/RGBA対応）
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            elif img.mode == "CMYK":
                img = img.convert("RGB")

            # リサイズ（設定ファイルから取得）
            max_width = self.config.get("max_width_px", 800)
            max_height = self.config.get("max_height_px", 600)
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # JPEG変換
            buffer = io.BytesIO()
            quality = self.config.get("quality", 85)
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            buffer.seek(0)

            # Base64エンコード
            encoded = base64.b64encode(buffer.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"

        except Exception:
            return None

    def generate_placeholder_svg(
        self, width: int, height: int, text: Optional[str] = None
    ) -> str:
        """
        プレースホルダーSVGを生成

        Args:
            width: 幅（px）
            height: 高さ（px）
            text: 表示テキスト

        Returns:
            str: SVG文字列
        """
        bg_color = self.config.get("placeholder_color", "#f3f4f6")
        display_text = text or self.config.get("placeholder_text", "写真なし")

        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="{bg_color}"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        font-family="Noto Sans JP, sans-serif" font-size="16" fill="#888">
    {display_text}
  </text>
</svg>"""

    def get_image_for_svg(
        self,
        property_id: int,
        db_connection,
        width: int = 800,
        height: int = 600,
    ) -> Dict[str, Any]:
        """
        SVG埋め込み用の画像データを取得

        Args:
            property_id: 物件ID
            db_connection: DB接続
            width: 表示幅
            height: 表示高さ

        Returns:
            dict: {
                "type": "base64" | "placeholder",
                "data": Base64文字列 | プレースホルダーSVG,
                "has_image": bool
            }
        """
        main_image = self.get_main_image(property_id, db_connection)

        if main_image:
            base64_data = self.image_to_base64(
                image_path=main_image.get("file_path"),
                image_url=main_image.get("file_url"),
            )
            if base64_data:
                return {
                    "type": "base64",
                    "data": base64_data,
                    "has_image": True,
                }

        # 画像がない場合はプレースホルダー
        return {
            "type": "placeholder",
            "data": self.generate_placeholder_svg(width, height),
            "has_image": False,
        }
