"""
汎用スクレイパー - 未知の不動産サイトでも自動的に物件情報を抽出
完全に構造を知らない状態から学習・抽出する
"""
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import numpy as np
from bs4 import BeautifulSoup, Tag
from loguru import logger
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from src.config.database import db_manager
from src.scrapers.base.base_scraper import BaseScraper
from src.utils.decorators import handle_errors, measure_time, retry


class UniversalScraper(BaseScraper):
    """未知のサイトでも対応できる汎用スクレイパー"""

    def __init__(self, site_name: str = "unknown", base_url: str = ""):
        super().__init__(site_name=site_name, base_url=base_url, login_required=False)

        # 日本の不動産サイトでよく使われるパターン
        self.property_patterns = {
            "price": [
                r"(\d{1,5}(?:,\d{3})*(?:\.\d+)?)\s*万円",
                r"(\d+)億(\d+)万円",
                r"価格[:：]\s*(\d+(?:,\d{3})*)\s*円",
                r"¥\s*(\d+(?:,\d{3})*)",
            ],
            "address": [
                r"((?:東京都|神奈川県|千葉県|埼玉県|大阪府|京都府|兵庫県|愛知県|福岡県|北海道|[^\s]+県)[^\s]+(?:市|区|町|村)[^\s]*)",
                r"所在地[:：]\s*([^\s]+(?:都|道|府|県)[^\s]+)",
                r"住所[:：]\s*([^\s]+)",
            ],
            "area": [
                r"(\d+(?:\.\d+)?)\s*(?:m²|㎡|平米)",
                r"面積[:：]\s*(\d+(?:\.\d+)?)",
                r"(\d+(?:\.\d+)?)\s*坪",
            ],
            "floor_plan": [
                r"(\d+)LDK",
                r"(\d+)DK",
                r"(\d+)K",
                r"間取り[:：]\s*(\d+[LDK]+)",
            ],
            "building_type": [
                r"(マンション|一戸建て|戸建て|土地|アパート|ビル|店舗)",
                r"物件種別[:：]\s*([\u4e00-\u9fa5]+)",
            ],
            "construction_year": [
                r"築(\d+)年",
                r"(\d{4})年築",
                r"建築年[:：]\s*(\d{4})",
            ],
            "contractor_company": [
                r"(?:株式会社|有限会社|合同会社|[\(（]株[\)）]|[\(（]有[\)）])\s*([\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff]+)",
                r"会社名[:：]\s*([\u4e00-\u9fa5]+)",
                r"取扱[:：]\s*([\u4e00-\u9fa5]+)",
            ],
        }

        # 学習済みパターンの保存場所
        self.patterns_dir = Path(settings.BASE_DIR) / "learned_patterns"
        self.patterns_dir.mkdir(exist_ok=True)

        # サイト分析結果
        self.site_analysis = {
            "listing_patterns": [],
            "property_containers": [],
            "field_mappings": {},
            "confidence_scores": {},
        }

    @measure_time
    def analyze_page_structure(self, html: str) -> Dict[str, Any]:
        """ページ構造を分析して物件リストのパターンを発見"""
        soup = BeautifulSoup(html, "html.parser")

        # 1. 繰り返し要素を検出（物件リストの可能性）
        repeated_elements = self._find_repeated_elements(soup)

        # 2. 各繰り返し要素を分析
        property_candidates = []
        for element_group in repeated_elements:
            if len(element_group) >= 3:  # 3つ以上の繰り返しがある場合
                score = self._evaluate_property_likelihood(element_group)
                if score > 0.5:
                    property_candidates.append(
                        {
                            "elements": element_group,
                            "score": score,
                            "selector": self._get_element_selector(element_group[0]),
                        }
                    )

        # 3. 最も可能性の高いパターンを選択
        if property_candidates:
            best_candidate = max(property_candidates, key=lambda x: x["score"])
            self.site_analysis["property_containers"] = best_candidate["elements"]
            self.site_analysis["listing_selector"] = best_candidate["selector"]

            # フィールドマッピングを学習
            self._learn_field_mappings(best_candidate["elements"])

            logger.info(
                f"Found property pattern with confidence: {best_candidate['score']:.2%}"
            )
            return self.site_analysis

        logger.warning("No clear property pattern found")
        return {}

    def _find_repeated_elements(self, soup: BeautifulSoup) -> List[List[Tag]]:
        """繰り返し要素を検出"""
        # クラス名でグループ化
        class_groups = defaultdict(list)

        for element in soup.find_all(["div", "article", "li", "section"]):
            classes = element.get("class", [])
            if classes:
                class_key = " ".join(sorted(classes))
                class_groups[class_key].append(element)

        # 構造が似ている要素をグループ化
        repeated_groups = []
        for class_name, elements in class_groups.items():
            if len(elements) >= 3:
                # 構造の類似性をチェック
                if self._have_similar_structure(elements):
                    repeated_groups.append(elements)

        return repeated_groups

    def _have_similar_structure(self, elements: List[Tag]) -> bool:
        """要素群が似た構造を持つかチェック"""
        if not elements:
            return False

        # 最初の要素の構造を基準にする
        base_structure = self._get_element_structure(elements[0])

        # 他の要素と比較
        for element in elements[1:]:
            structure = self._get_element_structure(element)
            similarity = self._calculate_structure_similarity(base_structure, structure)
            if similarity < 0.8:  # 80%以上の類似性が必要
                return False

        return True

    def _get_element_structure(self, element: Tag) -> Dict[str, Any]:
        """要素の構造を抽出"""
        structure = {
            "tag": element.name,
            "classes": sorted(element.get("class", [])),
            "children": [],
            "text_length": len(element.get_text(strip=True)),
            "has_link": bool(element.find("a")),
            "has_image": bool(element.find("img")),
        }

        # 子要素の構造
        for child in element.find_all(recursive=False):
            structure["children"].append(
                {"tag": child.name, "classes": sorted(child.get("class", []))}
            )

        return structure

    def _calculate_structure_similarity(self, struct1: Dict, struct2: Dict) -> float:
        """構造の類似度を計算"""
        score = 0.0

        # タグ名の一致
        if struct1["tag"] == struct2["tag"]:
            score += 0.3

        # クラスの一致度
        if struct1["classes"] == struct2["classes"]:
            score += 0.3

        # 子要素の類似度
        if len(struct1["children"]) == len(struct2["children"]):
            score += 0.2

        # テキスト長の類似度
        if abs(struct1["text_length"] - struct2["text_length"]) < 50:
            score += 0.1

        # リンク・画像の有無
        if struct1["has_link"] == struct2["has_link"]:
            score += 0.05
        if struct1["has_image"] == struct2["has_image"]:
            score += 0.05

        return score

    def _evaluate_property_likelihood(self, elements: List[Tag]) -> float:
        """要素群が物件リストである可能性を評価"""
        scores = []

        for element in elements[:5]:  # 最初の5つをサンプル
            text = element.get_text()
            element_score = 0.0

            # 価格パターンの存在
            for pattern in self.property_patterns["price"]:
                if re.search(pattern, text):
                    element_score += 0.3
                    break

            # 住所パターンの存在
            for pattern in self.property_patterns["address"]:
                if re.search(pattern, text):
                    element_score += 0.3
                    break

            # 面積・間取りパターン
            for pattern_type in ["area", "floor_plan"]:
                for pattern in self.property_patterns[pattern_type]:
                    if re.search(pattern, text):
                        element_score += 0.2
                        break

            scores.append(element_score)

        # 平均スコアを返す
        return np.mean(scores) if scores else 0.0

    def _get_element_selector(self, element: Tag) -> str:
        """要素のCSSセレクタを生成"""
        classes = element.get("class", [])
        if classes:
            return f"{element.name}.{'.'.join(classes)}"

        # IDがある場合
        if element.get("id"):
            return f"{element.name}#{element['id']}"

        # 親要素のクラスを使用
        parent = element.parent
        if parent and parent.get("class"):
            parent_classes = ".".join(parent.get("class", []))
            return f".{parent_classes} > {element.name}"

        return element.name

    def _learn_field_mappings(self, property_elements: List[Tag]):
        """物件要素からフィールドマッピングを学習"""
        field_candidates = defaultdict(list)

        for element in property_elements[:10]:  # 最初の10個をサンプル
            # 各フィールドタイプを検索
            for field_type, patterns in self.property_patterns.items():
                for pattern in patterns:
                    # テキスト全体から検索
                    text_matches = re.findall(pattern, element.get_text())
                    if text_matches:
                        # マッチした要素を特定
                        for match_element in element.find_all(text=re.compile(pattern)):
                            parent = match_element.parent
                            if parent:
                                selector = self._get_specific_selector(parent, element)
                                field_candidates[field_type].append(
                                    {
                                        "selector": selector,
                                        "confidence": 1.0,
                                        "sample": text_matches[0],
                                    }
                                )

        # 最も頻出するセレクタを選択
        for field_type, candidates in field_candidates.items():
            if candidates:
                # セレクタの出現頻度を計算
                selector_counts = Counter(c["selector"] for c in candidates)
                best_selector = selector_counts.most_common(1)[0][0]

                self.site_analysis["field_mappings"][field_type] = {
                    "selector": best_selector,
                    "confidence": selector_counts[best_selector] / len(candidates),
                    "samples": [
                        c["sample"]
                        for c in candidates
                        if c["selector"] == best_selector
                    ][:3],
                }

        logger.info(
            f"Learned field mappings: {list(self.site_analysis['field_mappings'].keys())}"
        )

    def _get_specific_selector(self, element: Tag, container: Tag) -> str:
        """コンテナ内での特定のセレクタを生成"""
        # クラスベースのセレクタ
        classes = element.get("class", [])
        if classes:
            return f".{'.'.join(classes)}"

        # タグ名と位置ベース
        tag_name = element.name
        siblings = [
            e for e in container.find_all(tag_name) if e.parent == element.parent
        ]
        if len(siblings) > 1:
            position = siblings.index(element) + 1
            return f"{tag_name}:nth-of-type({position})"

        return tag_name

    @retry(max_attempts=3)
    def scrape_listing_page(self, url: str) -> List[Dict[str, Any]]:
        """物件一覧ページをスクレイピング"""
        logger.info(f"Universal scraping: {url}")

        html = self.get_page_source(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        # 学習済みパターンを読み込む
        learned_patterns = self._load_learned_patterns()

        if learned_patterns:
            # 学習済みパターンで抽出
            return self._extract_with_learned_patterns(soup, learned_patterns)
        else:
            # 新規学習モード
            logger.info("No learned patterns found. Starting analysis...")

            # ページ構造を分析
            self.analyze_page_structure(html)

            if self.site_analysis.get("property_containers"):
                # 分析結果を使って抽出
                properties = self._extract_properties_from_analysis(soup)

                # 学習結果を保存
                if properties:
                    self._save_learned_patterns()

                return properties

        return []

    def _extract_properties_from_analysis(
        self, soup: BeautifulSoup
    ) -> List[Dict[str, Any]]:
        """分析結果を使って物件情報を抽出"""
        properties = []

        # 物件コンテナを取得
        selector = self.site_analysis.get("listing_selector", "")
        if not selector:
            return []

        property_elements = soup.select(selector)
        logger.info(
            f"Found {len(property_elements)} property elements with selector: {selector}"
        )

        for element in property_elements:
            property_data = self._extract_property_from_element(element)
            if property_data and self._is_valid_property(property_data):
                properties.append(property_data)

        return properties

    def _extract_property_from_element(self, element: Tag) -> Optional[Dict[str, Any]]:
        """単一の要素から物件情報を抽出"""
        property_data = {
            "source_site": self.site_name,
            "transaction_type": "売買",
            "scraped_at": datetime.now().isoformat(),
            "extraction_confidence": 0.0,
        }

        confidence_scores = []

        # フィールドマッピングを使って抽出
        for field_type, mapping in self.site_analysis["field_mappings"].items():
            selector = mapping["selector"]

            try:
                # セレクタで要素を検索
                field_element = element.select_one(selector)
                if field_element:
                    text = field_element.get_text(strip=True)

                    # パターンマッチングで値を抽出
                    extracted_value = self._extract_field_value(field_type, text)
                    if extracted_value:
                        property_data[
                            self._get_field_name(field_type)
                        ] = extracted_value
                        confidence_scores.append(mapping["confidence"])

            except Exception as e:
                logger.debug(f"Error extracting {field_type}: {e}")

        # 詳細URLを抽出
        link = element.select_one("a[href]")
        if link:
            property_data["source_url"] = urljoin(self.base_url, link["href"])
            property_data["listing_id"] = self._extract_id_from_url(link["href"])

        # 信頼度スコアを計算
        if confidence_scores:
            property_data["extraction_confidence"] = np.mean(confidence_scores)

        return property_data

    def _extract_field_value(self, field_type: str, text: str) -> Optional[Any]:
        """フィールドタイプに応じて値を抽出"""
        patterns = self.property_patterns.get(field_type, [])

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if field_type == "price":
                    return self._parse_price(match.group(0))
                elif field_type == "area":
                    return self._parse_area(match.group(1))
                elif field_type == "construction_year":
                    return self._parse_year(match.group(1))
                else:
                    return match.group(1).strip()

        return None

    def _get_field_name(self, field_type: str) -> str:
        """フィールドタイプをデータベースカラム名に変換"""
        mapping = {
            "price": "price",
            "address": "address",
            "area": "building_area",
            "floor_plan": "floor_plan",
            "building_type": "property_type",
            "construction_year": "construction_year",
            "contractor_company": "contractor_company_name",
        }
        return mapping.get(field_type, field_type)

    def _parse_price(self, price_text: str) -> Optional[float]:
        """価格をパース（売買専用）"""
        # 賃料除外
        if any(keyword in price_text for keyword in ["賃", "家賃", "/月"]):
            return None

        # 億万円
        match = re.search(r"(\d+)億(\d+)万", price_text)
        if match:
            return float(match.group(1)) * 100000000 + float(match.group(2)) * 10000

        # 万円
        match = re.search(r"(\d+(?:,\d+)*)\s*万", price_text)
        if match:
            num_str = match.group(1).replace(",", "")
            return float(num_str) * 10000

        return None

    def _parse_area(self, area_text: str) -> Optional[float]:
        """面積をパース"""
        try:
            # 坪を㎡に変換
            if "坪" in area_text:
                return float(area_text) * 3.30579
            else:
                return float(area_text)
        except:
            return None

    def _parse_year(self, year_text: str) -> Optional[int]:
        """年をパース"""
        try:
            year = int(year_text)
            # 築年数の場合は現在年から引く
            if year < 100:
                return datetime.now().year - year
            return year
        except:
            return None

    def _extract_id_from_url(self, url: str) -> str:
        """URLから物件IDを抽出"""
        # 数字の連続を探す
        matches = re.findall(r"/(\d{5,})", url)
        if matches:
            return f"{self.site_name}_{matches[-1]}"

        # URLのハッシュ値を使用
        import hashlib

        url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
        return f"{self.site_name}_{url_hash}"

    def _is_valid_property(self, property_data: Dict[str, Any]) -> bool:
        """物件データの妥当性をチェック"""
        # 最低限必要なフィールド
        if not property_data.get("price"):
            return False

        # 価格の妥当性
        price = property_data.get("price", 0)
        if price < 1000000 or price > 10000000000:
            return False

        # 信頼度チェック
        if property_data.get("extraction_confidence", 0) < 0.3:
            return False

        return True

    def _load_learned_patterns(self) -> Optional[Dict[str, Any]]:
        """学習済みパターンを読み込む"""
        pattern_file = self.patterns_dir / f"{self.site_name}_patterns.json"

        if pattern_file.exists():
            try:
                with open(pattern_file, "r", encoding="utf-8") as f:
                    patterns = json.load(f)
                logger.info(f"Loaded learned patterns for {self.site_name}")
                return patterns
            except Exception as e:
                logger.error(f"Error loading patterns: {e}")

        return None

    def _save_learned_patterns(self):
        """学習したパターンを保存"""
        pattern_file = self.patterns_dir / f"{self.site_name}_patterns.json"

        patterns = {
            "site_name": self.site_name,
            "base_url": self.base_url,
            "learned_at": datetime.now().isoformat(),
            "listing_selector": self.site_analysis.get("listing_selector", ""),
            "field_mappings": self.site_analysis.get("field_mappings", {}),
            "confidence_scores": self.site_analysis.get("confidence_scores", {}),
        }

        try:
            with open(pattern_file, "w", encoding="utf-8") as f:
                json.dump(patterns, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved learned patterns for {self.site_name}")

            # データベースにも保存
            db_manager.save_learning_data(
                {
                    "site_name": self.site_name,
                    "url_pattern": self.base_url,
                    "patterns": patterns,
                    "success_rate": 0.8,  # 初期値
                    "sample_count": len(
                        self.site_analysis.get("property_containers", [])
                    ),
                }
            )

        except Exception as e:
            logger.error(f"Error saving patterns: {e}")

    def _extract_with_learned_patterns(
        self, soup: BeautifulSoup, patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """学習済みパターンを使って抽出"""
        # パターンを適用
        self.site_analysis["listing_selector"] = patterns.get("listing_selector", "")
        self.site_analysis["field_mappings"] = patterns.get("field_mappings", {})

        # 抽出実行
        return self._extract_properties_from_analysis(soup)

    def scrape_detail_page(self, url: str) -> Optional[Dict[str, Any]]:
        """詳細ページから追加情報を抽出（実装予定）"""
        # TODO: 詳細ページの汎用抽出
        return None


# テスト実行
if __name__ == "__main__":
    # 未知のサイトでテスト
    scraper = UniversalScraper(
        site_name="test_site", base_url="https://example-realestate.com"
    )

    # テスト用HTML
    test_html = """
    <div class="property-list">
        <div class="property-item">
            <h3>東京都渋谷区の新築マンション</h3>
            <p class="price">3,980万円</p>
            <p class="details">3LDK / 75.5㎡</p>
            <p class="company">株式会社テスト不動産</p>
        </div>
        <div class="property-item">
            <h3>世田谷区の中古一戸建て</h3>
            <p class="price">5,480万円</p>
            <p class="details">4LDK / 120㎡</p>
            <p class="company">有限会社サンプル住宅</p>
        </div>
    </div>
    """

    # 構造分析
    analysis = scraper.analyze_page_structure(test_html)
    if analysis:
        print("✓ Page structure analyzed successfully")
        print(f"  Field mappings: {list(analysis.get('field_mappings', {}).keys())}")
    else:
        print("✗ Failed to analyze page structure")
