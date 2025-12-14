"""
登記事項証明書PDF テキスト抽出モジュール
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    logger.warning("pdfplumber not installed. Run: pip install pdfplumber")


class ToukiPDFExtractor:
    """登記事項証明書PDFからテキストを抽出するクラス"""

    def __init__(self, upload_dir: str = None):
        """
        Args:
            upload_dir: PDFファイルの保存先ディレクトリ
        """
        if upload_dir is None:
            # デフォルトはrea-scraper/uploads/touki/
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            upload_dir = os.path.join(base_dir, 'uploads', 'touki')

        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

        if pdfplumber is None:
            raise ImportError("pdfplumber is required. Install with: pip install pdfplumber")

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        PDFからテキストを抽出

        Args:
            pdf_path: PDFファイルのパス

        Returns:
            抽出したテキスト（失敗時はNone）
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None

        try:
            all_text = []

            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"PDF pages: {len(pdf.pages)}")

                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        all_text.append(f"--- Page {i + 1} ---\n{text}")
                        logger.debug(f"Page {i + 1}: {len(text)} chars extracted")

            full_text = "\n\n".join(all_text)
            logger.info(f"Total extracted: {len(full_text)} chars from {len(pdf.pages)} pages")

            return full_text

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None

    def extract_with_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        PDFからテキストとメタデータを抽出

        Args:
            pdf_path: PDFファイルのパス

        Returns:
            {
                'raw_text': 抽出テキスト,
                'page_count': ページ数,
                'file_size': ファイルサイズ,
                'extracted_at': 抽出日時
            }
        """
        result = {
            'raw_text': None,
            'page_count': 0,
            'file_size': 0,
            'extracted_at': datetime.now().isoformat(),
            'error': None
        }

        if not os.path.exists(pdf_path):
            result['error'] = f"File not found: {pdf_path}"
            return result

        result['file_size'] = os.path.getsize(pdf_path)

        try:
            all_text = []

            with pdfplumber.open(pdf_path) as pdf:
                result['page_count'] = len(pdf.pages)

                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        all_text.append(f"--- Page {i + 1} ---\n{text}")

            result['raw_text'] = "\n\n".join(all_text)

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error extracting PDF: {e}")

        return result

    def save_uploaded_file(self, file_content: bytes, original_filename: str) -> str:
        """
        アップロードされたファイルを保存

        Args:
            file_content: ファイルの内容（バイナリ）
            original_filename: 元のファイル名

        Returns:
            保存先のファイルパス
        """
        # タイムスタンプ付きファイル名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{original_filename}"
        file_path = os.path.join(self.upload_dir, safe_filename)

        with open(file_path, 'wb') as f:
            f.write(file_content)

        logger.info(f"Saved uploaded file: {file_path}")
        return file_path


# テスト用
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <pdf_file>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    extractor = ToukiPDFExtractor()

    result = extractor.extract_with_metadata(pdf_path)

    if result['error']:
        print(f"Error: {result['error']}")
    else:
        print(f"Pages: {result['page_count']}")
        print(f"Size: {result['file_size']} bytes")
        print(f"\n=== Extracted Text ===\n")
        print(result['raw_text'][:2000] if result['raw_text'] else "No text extracted")
        if result['raw_text'] and len(result['raw_text']) > 2000:
            print(f"\n... ({len(result['raw_text']) - 2000} more chars)")
