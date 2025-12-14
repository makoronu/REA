"""
登記事項証明書 パーサーモジュール
抽出したテキストを構造化データに変換

対応フォーマット:
- 登記情報提供サービスからのPDF（罫線テーブル形式）
- 土地全部事項証明書
- 建物全部事項証明書

注意事項:
- PDFテキスト抽出では下線情報が失われるため、抹消事項の判別は不可
- 履歴がある場合は最新の情報を抽出
"""
import re
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ToukiParser:
    """登記事項証明書テキストをパースして構造化データに変換"""

    def __init__(self):
        # 全角→半角変換テーブル
        self.zenkaku_to_hankaku = str.maketrans(
            '０１２３４５６７８９：．，',
            '0123456789:.,'
        )

    def normalize(self, text: str) -> str:
        """全角数字を半角に変換"""
        return text.translate(self.zenkaku_to_hankaku)

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
            'real_estate_number': self._extract_real_estate_number(raw_text),
            'land_info': {},
            'building_info': {},
            'owner_info': {},
            'mortgage_info': [],
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

            # 所有者情報の抽出（甲区から）
            result['owner_info'] = self._extract_owner_info(raw_text)

            # 抵当権情報の抽出（乙区から）
            result['mortgage_info'] = self._extract_mortgage_info(raw_text)

            # 信頼度の計算
            result['confidence'] = self._calculate_confidence(result)

            logger.info(f"Parsed: type={result['document_type']}, confidence={result['confidence']:.2f}")

        except Exception as e:
            logger.error(f"Error parsing text: {e}")
            result['error'] = str(e)

        return result

    def _detect_document_type(self, text: str) -> str:
        """登記の種類を判定（土地/建物/両方）"""
        has_land = '土地の表示' in text
        has_building = '建物の表示' in text or '主である建物の表示' in text

        if has_land and has_building:
            return 'both'
        elif has_building:
            return 'building'
        elif has_land:
            return 'land'
        else:
            return 'unknown'

    def _extract_real_estate_number(self, text: str) -> Optional[str]:
        """不動産番号を抽出"""
        match = re.search(r'不動産番号[│\|]?\s*([０-９\d]+)', text)
        return self.normalize(match.group(1)) if match else None

    def _extract_land_info(self, text: str) -> Dict[str, Any]:
        """土地情報を抽出"""
        info = {}

        # 所在（最新）- 日付情報を除外
        matches = re.findall(r'所\s*在[│\|]([^│┃\n]+)', text)
        if matches:
            for loc in reversed(matches):
                loc = loc.strip()
                if loc and not re.search(r'年|月|日|変更|登記', loc):
                    info['location'] = loc
                    break

        # 地番 - 最初にマッチしたもの
        match = re.search(r'([０-９\d]+番[０-９\d]*)\s*│', text)
        if match:
            info['lot_number'] = self.normalize(match.group(1))

        # 地目（最新）- 最後にマッチしたものを使用
        land_categories = ['宅地', '畑', '田', '山林', '原野', '雑種地', '公衆用道路', '墓地', '池沼']
        for cat in land_categories:
            # │宅地│ または │ 宅地 │ のパターン
            if f'│{cat}' in text or f'│ {cat}' in text:
                # 最後に出現したものを採用
                last_pos = max(text.rfind(f'│{cat}'), text.rfind(f'│ {cat}'))
                if last_pos > info.get('_cat_pos', -1):
                    info['land_category'] = cat
                    info['_cat_pos'] = last_pos
        # 一時的なキーを削除
        info.pop('_cat_pos', None)

        # 地積: │ 数字：数字 │ パターン
        area_matches = re.findall(r'│\s*([０-９\d]+)[：:]([０-９\d]+)\s*│', text)
        if area_matches:
            # 最後のマッチを使用（最新の地積）
            whole, decimal = area_matches[-1]
            area = float(self.normalize(whole)) + float(self.normalize(decimal)) / 100
            info['land_area_m2'] = round(area, 2)
        else:
            # │ 数字： │ のパターン（小数点以下なし）
            area_match = re.search(r'│\s*([０-９\d]+)[：:]\s*│', text)
            if area_match:
                info['land_area_m2'] = float(self.normalize(area_match.group(1)))

        return info

    def _extract_building_info(self, text: str) -> Dict[str, Any]:
        """建物情報を抽出"""
        info = {}

        # 所在
        matches = re.findall(r'所\s*在[│\|]([^│┃\n]+)', text)
        if matches:
            for loc in reversed(matches):
                loc = loc.strip()
                if loc and not re.search(r'年|月|日|変更|登記', loc):
                    info['location'] = loc
                    break

        # 家屋番号
        match = re.search(r'家屋番号[│\|]\s*([^│┃\n]+)', text)
        if match:
            info['building_number'] = self.normalize(match.group(1).strip())

        # 種類
        building_types = ['居宅', '共同住宅', '店舗', '事務所', '倉庫', '工場', '車庫']
        for bt in building_types:
            if bt in text:
                info['building_type'] = bt
                break

        # 構造: │木造...階│ + 「建」
        match = re.search(r'│(木造[^│\n]+階)', text)
        if match:
            structure = match.group(1)
            # 「建」が含まれていなければ追加
            if not structure.endswith('建'):
                structure += '建'
            info['structure'] = structure
        else:
            # 鉄骨造、鉄筋コンクリート造なども対応
            match = re.search(r'│((?:鉄骨|鉄筋コンクリート|鉄骨鉄筋コンクリート)[^│\n]+階)', text)
            if match:
                structure = match.group(1)
                if not structure.endswith('建'):
                    structure += '建'
                info['structure'] = structure

        # 床面積: X階 数字：数字
        floor_matches = re.findall(r'([１２３４５６７８９\d]+)階\s*([０-９\d]+)[：:]([０-９\d]+)', text)
        if floor_matches:
            floor_areas = {}
            total = 0.0
            for floor, whole, decimal in floor_matches:
                floor_num = int(self.normalize(floor))
                area = float(self.normalize(whole)) + float(self.normalize(decimal)) / 100
                floor_areas[f'floor_{floor_num}'] = round(area, 2)
                total += area
            info['floor_areas'] = floor_areas
            info['total_floor_area_m2'] = round(total, 2)

        # 新築年月日
        match = re.search(r'(明治|大正|昭和|平成|令和)([０-９\d]+)年([０-９\d]+)月([０-９\d]+)日新築', text)
        if match:
            era, year, month, day = match.groups()
            info['construction_date'] = self._convert_japanese_date(era, year, month, day)

        return info

    def _extract_owner_info(self, text: str) -> Dict[str, Any]:
        """所有者情報を抽出（甲区から最新の所有者）"""
        info = {}

        # パターン1: 所有者 住所\n 名前
        # 例: 所有者 北見市川東５６番地６\n        鈴 木 敏 文
        matches = re.findall(
            r'所有者\s+([^\n│┃]+?)(?:\s*┃|\s*│|\n)\s*(?:│\s*)*([^\n│┃]+?)(?:\s*┃|\s*│|\n)',
            text
        )

        if matches:
            # 最後の所有者情報を使用（最新）
            for address, name in reversed(matches):
                address = address.strip()
                name = re.sub(r'\s+', '', name.strip())
                # 有効な名前かチェック（数字や記号のみは除外）
                if name and not re.match(r'^[０-９\d：:]+$', name):
                    info['owner_address'] = address
                    info['owner_name'] = name
                    break

        return info

    def _extract_mortgage_info(self, text: str) -> List[Dict[str, Any]]:
        """抵当権情報を抽出（乙区）"""
        mortgages = []

        # 抵当権設定のパターン
        if '抵当権設定' not in text:
            return mortgages

        # 債権額を抽出
        amount_matches = re.findall(r'債権額\s*金([０-９\d,，]+)万?円', text)
        holder_matches = re.findall(r'抵当権者\s+([^\n│┃]+)', text)

        for i, amount_str in enumerate(amount_matches):
            amount_str = self.normalize(amount_str).replace(',', '')
            amount = int(amount_str)
            # 万円の場合は10000倍
            # （テキスト内で「万円」が金額の後にあるかで判断）

            mortgage = {
                'type': '抵当権',
                'amount': amount,
            }

            if i < len(holder_matches):
                mortgage['holder'] = holder_matches[i].strip()

            mortgages.append(mortgage)

        return mortgages

    def _convert_japanese_date(self, era: str, year: str, month: str, day: str) -> str:
        """和暦を西暦に変換"""
        era_start = {
            '明治': 1868,
            '大正': 1912,
            '昭和': 1926,
            '平成': 1989,
            '令和': 2019,
        }

        year_num = int(self.normalize(year))
        month_num = int(self.normalize(month))
        day_num = int(self.normalize(day))

        western_year = era_start.get(era, 1900) + year_num - 1

        return f"{western_year}-{month_num:02d}-{day_num:02d}"

    def _calculate_confidence(self, result: Dict) -> float:
        """パース結果の信頼度を計算（0.0-1.0）"""
        score = 0.0
        max_score = 0.0

        # 不動産番号
        max_score += 1
        if result.get('real_estate_number'):
            score += 1

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
            if land.get('land_area_m2'):
                score += 1

        # 建物情報のスコア
        if result['document_type'] in ['building', 'both']:
            max_score += 5
            building = result.get('building_info', {})
            if building.get('location'):
                score += 1
            if building.get('building_number'):
                score += 1
            if building.get('building_type'):
                score += 1
            if building.get('structure'):
                score += 1
            if building.get('total_floor_area_m2'):
                score += 1

        # 所有者情報
        max_score += 2
        owner = result.get('owner_info', {})
        if owner.get('owner_name'):
            score += 1
        if owner.get('owner_address'):
            score += 1

        if max_score == 0:
            return 0.0

        return round(score / max_score, 2)

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

        # 不動産番号
        if parsed_data.get('real_estate_number'):
            property_data['real_estate_number'] = parsed_data['real_estate_number']

        # 土地情報からマッピング
        land = parsed_data.get('land_info', {})
        if land.get('location'):
            property_data['address'] = land['location']
        if land.get('lot_number'):
            property_data['lot_number'] = land['lot_number']
        if land.get('land_area_m2'):
            property_data['land_area_m2'] = land['land_area_m2']
        if land.get('land_category'):
            property_data['land_category'] = land['land_category']

        # 建物情報からマッピング
        building = parsed_data.get('building_info', {})
        if building.get('location') and not property_data.get('address'):
            property_data['address'] = building['location']
        if building.get('structure'):
            property_data['building_structure'] = building['structure']
        if building.get('total_floor_area_m2'):
            property_data['total_floor_area_m2'] = building['total_floor_area_m2']
        if building.get('building_type'):
            property_data['building_type'] = building['building_type']
        if building.get('construction_date'):
            property_data['construction_date'] = building['construction_date']
        if building.get('floor_areas'):
            property_data['floor_areas'] = building['floor_areas']

        # 所有者情報
        owner = parsed_data.get('owner_info', {})
        if owner.get('owner_name'):
            property_data['owner_name'] = owner['owner_name']
        if owner.get('owner_address'):
            property_data['owner_address'] = owner['owner_address']

        return property_data


# テスト用
if __name__ == "__main__":
    import sys
    import json

    sample_text = """
    ┃ 表 題 部 （土地の表示） │調製│平成１７年６月２７日 │不動産番号│４６０３０００２４０９６５┃
    ┃所 在│北見市東三輪一丁目 │平成２０年１１月８日変更 ┃
    ┃ ① 地 番 │ ②地 目 │ ③ 地 積 ㎡ │ 原因及びその日付〔登記の日付〕 ┃
    ┃９１番４４ │宅地 │ １８１：８０│②③昭和４８年５月１０日地目変更 ┃
    ┃所有者 北見市川東５６番地６
    ┃        鈴 木 敏 文
    """

    parser = ToukiParser()
    result = parser.parse(sample_text)

    print("=== Parse Result ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n=== Property Data ===")
    property_data = parser.to_property_data(result)
    print(json.dumps(property_data, ensure_ascii=False, indent=2))
