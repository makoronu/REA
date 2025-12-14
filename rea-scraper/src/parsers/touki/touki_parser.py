"""
登記事項証明書 パーサーモジュール
抽出したテキストを構造化データに変換
"""
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger


class ToukiParser:
    """登記事項証明書テキストをパースして構造化データに変換"""

    def __init__(self):
        # 土地用の正規表現パターン
        self.land_patterns = {
            'location': r'所在[　\s]+(.+?)(?:\n|$)',
            'lot_number': r'地番[　\s]+(.+?)(?:\n|$)',
            'land_category': r'地目[　\s]+(.+?)(?:\n|$)',
            'land_area': r'地積[　\s]+([\d,.]+)(?:㎡|平方メートル)?',
        }

        # 建物用の正規表現パターン
        self.building_patterns = {
            'location': r'所在[　\s]+(.+?)(?:\n|$)',
            'building_number': r'家屋番号[　\s]+(.+?)(?:\n|$)',
            'building_type': r'種類[　\s]+(.+?)(?:\n|$)',
            'structure': r'構造[　\s]+(.+?)(?:\n|$)',
            'floor_area': r'床面積[　\s]+([\d,.]+)(?:㎡|平方メートル)?',
        }

        # 所有者情報パターン
        self.owner_patterns = {
            'owner_name': r'所有者[　\s]+(.+?)(?:\n|$)',
            'owner_address': r'住所[　\s]+(.+?)(?:\n|$)',
        }

    def parse(self, raw_text: str) -> Dict[str, Any]:
        """
        生テキストをパースして構造化データに変換

        Args:
            raw_text: PDFから抽出した生テキスト

        Returns:
            構造化されたデータ（JSON形式）
        """
        if not raw_text:
            return {'error': 'Empty text', 'parsed_at': datetime.now().isoformat()}

        result = {
            'document_type': self._detect_document_type(raw_text),
            'land_info': {},
            'building_info': {},
            'owner_info': {},
            'raw_sections': {},
            'parsed_at': datetime.now().isoformat(),
            'confidence': 0.0,
        }

        try:
            # 土地情報の抽出
            if result['document_type'] in ['land', 'both']:
                result['land_info'] = self._extract_land_info(raw_text)

            # 建物情報の抽出
            if result['document_type'] in ['building', 'both']:
                result['building_info'] = self._extract_building_info(raw_text)

            # 所有者情報の抽出
            result['owner_info'] = self._extract_owner_info(raw_text)

            # 信頼度の計算
            result['confidence'] = self._calculate_confidence(result)

            logger.info(f"Parsed document type: {result['document_type']}, confidence: {result['confidence']:.2f}")

        except Exception as e:
            logger.error(f"Error parsing text: {e}")
            result['error'] = str(e)

        return result

    def _detect_document_type(self, text: str) -> str:
        """登記の種類を判定（土地/建物/両方）"""
        has_land = '土地の表示' in text or '地番' in text
        has_building = '建物の表示' in text or '家屋番号' in text

        if has_land and has_building:
            return 'both'
        elif has_building:
            return 'building'
        elif has_land:
            return 'land'
        else:
            return 'unknown'

    def _extract_land_info(self, text: str) -> Dict[str, Any]:
        """土地情報を抽出"""
        info = {}

        for key, pattern in self.land_patterns.items():
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                # 面積の場合は数値に変換
                if key == 'land_area':
                    value = self._parse_area(value)
                info[key] = value

        return info

    def _extract_building_info(self, text: str) -> Dict[str, Any]:
        """建物情報を抽出"""
        info = {}

        for key, pattern in self.building_patterns.items():
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                # 面積の場合は数値に変換
                if key == 'floor_area':
                    value = self._parse_area(value)
                info[key] = value

        return info

    def _extract_owner_info(self, text: str) -> Dict[str, Any]:
        """所有者情報を抽出"""
        info = {}

        for key, pattern in self.owner_patterns.items():
            match = re.search(pattern, text)
            if match:
                info[key] = match.group(1).strip()

        return info

    def _parse_area(self, area_str: str) -> Optional[float]:
        """面積文字列を数値に変換"""
        try:
            # カンマ除去、全角→半角
            cleaned = area_str.replace(',', '').replace('，', '')
            cleaned = cleaned.translate(str.maketrans('０１２３４５６７８９．', '0123456789.'))
            return float(cleaned)
        except (ValueError, AttributeError):
            return None

    def _calculate_confidence(self, result: Dict) -> float:
        """パース結果の信頼度を計算（0.0-1.0）"""
        score = 0.0
        max_score = 0.0

        # 土地情報のスコア
        if result['document_type'] in ['land', 'both']:
            max_score += 4
            land = result.get('land_info', {})
            if land.get('location'):
                score += 1
            if land.get('lot_number'):
                score += 1
            if land.get('land_category'):
                score += 1
            if land.get('land_area'):
                score += 1

        # 建物情報のスコア
        if result['document_type'] in ['building', 'both']:
            max_score += 4
            building = result.get('building_info', {})
            if building.get('location'):
                score += 1
            if building.get('building_number'):
                score += 1
            if building.get('structure'):
                score += 1
            if building.get('floor_area'):
                score += 1

        if max_score == 0:
            return 0.0

        return score / max_score

    def to_property_data(self, parsed_data: Dict) -> Dict[str, Any]:
        """
        パース結果をpropertiesテーブル形式に変換

        Args:
            parsed_data: parseメソッドの戻り値

        Returns:
            propertiesテーブルに保存できる形式のデータ
        """
        property_data = {
            'source_site': 'touki',
            'transaction_type': '売買',
            'created_at': datetime.now().isoformat(),
        }

        # 土地情報からマッピング
        land = parsed_data.get('land_info', {})
        if land.get('location'):
            property_data['address'] = land['location']
        if land.get('lot_number'):
            property_data['lot_number'] = land['lot_number']
        if land.get('land_area'):
            property_data['land_area_m2'] = land['land_area']

        # 建物情報からマッピング
        building = parsed_data.get('building_info', {})
        if building.get('location') and not property_data.get('address'):
            property_data['address'] = building['location']
        if building.get('structure'):
            property_data['building_structure'] = building['structure']
        if building.get('floor_area'):
            property_data['total_floor_area_m2'] = building['floor_area']

        # 所有者情報
        owner = parsed_data.get('owner_info', {})
        if owner.get('owner_name'):
            property_data['owner_name'] = owner['owner_name']

        return property_data


# テスト用
if __name__ == "__main__":
    # サンプルテキストでテスト
    sample_text = """
    表題部（土地の表示）
    所在　北海道札幌市中央区大通西１丁目
    地番　１２３番４
    地目　宅地
    地積　１５０．２５㎡

    甲区（所有権に関する事項）
    所有者　山田太郎
    住所　北海道札幌市北区北１条西２丁目
    """

    parser = ToukiParser()
    result = parser.parse(sample_text)

    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n=== Property Data ===")
    property_data = parser.to_property_data(result)
    print(json.dumps(property_data, ensure_ascii=False, indent=2))
