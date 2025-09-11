"""
ホームズ不動産売買物件スクレイパー
共通ライブラリ最大活用版
"""
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from loguru import logger

# パス設定（より簡潔に）
project_root = Path(__file__).resolve()
while project_root.name != "REA" and project_root.parent != project_root:
    project_root = project_root.parent

if project_root.name != "REA":
    raise ValueError("REAプロジェクトルートが見つかりません")

rea_scraper_root = project_root / "rea-scraper"
sys.path.insert(0, str(project_root))
sys.path.insert(1, str(rea_scraper_root))

# 既存モジュール
from src.scrapers.base.base_scraper import BaseScraper
from src.utils.decorators import retry

from shared.database import READatabase
from shared.formatters import clean_phone_number, extract_listing_id, normalize_address
from shared.real_estate_utils import (
    determine_property_type,
    parse_area,
    parse_construction_year,
    parse_sale_price,
)

# 共通ライブラリインポート
from shared.scrapers_common import (
    RateLimiter,
    URLQueue,
    create_property_base_data,
    extract_contractor_info,
)


class HomesPropertyScraper(BaseScraper):
    """ホームズ売買物件専用スクレイパー（共通ライブラリ使用版）"""

    def __init__(self):
        super().__init__(
            site_name="homes", base_url="https://www.homes.co.jp", login_required=False
        )

        self.url_queue = URLQueue(site_name="homes")
        self.rate_limiter = RateLimiter(min_delay=3.0, max_delay=8.0)

        # ホームズ固有のセレクタ
        self.selectors = {
            "property_link": 'a[href*="/kodate/b-"], a[href*="/mansion/b-"], a[href*="/tochi/b-"]',
            "next_page": ['a:contains("次へ")', "a.next", ".pagination__next a"],
            "detail_title": "h1.name, h1",
            "company_name": ".shopName",
            "company_phone": ".freeCall, span.u-text-2xl",
        }

        # テーブルマッピング定義
        self.table_mapping = {
            "所在地": (
                "address",
                lambda v: normalize_address(re.sub(r"(地図を見る|無料).*", "", v).strip()),
            ),
            "土地面積": ("land_area", parse_area),
            "建物面積": ("building_area", parse_area),
            "築年月": ("construction_year", parse_construction_year),
            "構造": ("structure", lambda v: v),
        }

    def collect_property_urls(self, base_url: str, max_pages: int = 50) -> int:
        """Step 1: 物件URLを収集"""
        logger.info(f"🕷️ [Homes] URL収集開始: {base_url}")
        collected_urls = []
        current_url = base_url

        for page_num in range(1, max_pages + 1):
            logger.info(f"📄 Page {page_num}: {current_url}")

            html = self.get_page_source(current_url)
            if not html:
                break

            soup = BeautifulSoup(html, "html.parser")

            # 物件リンク収集
            links = soup.select(self.selectors["property_link"])
            page_urls = [
                urljoin(self.base_url, link["href"])
                for link in links
                if link.get("href")
            ]
            collected_urls.extend(page_urls)

            logger.info(f"✅ Found {len(page_urls)} properties")

            # 次ページ
            next_link = self._find_next_page(soup, current_url)
            if not next_link:
                break

            current_url = next_link
            self.rate_limiter.wait()

        new_count = self.url_queue.add_urls(collected_urls)
        logger.info(f"🎯 収集完了: {new_count}件の新規URL")
        return new_count

    def process_batch(
        self, batch_size: int = 10, save_to_db: bool = False
    ) -> List[Dict[str, Any]]:
        """Step 2: バッチ処理"""
        urls = self.url_queue.get_next_batch(batch_size)
        if not urls:
            return []

        properties = []
        for i, url in enumerate(urls, 1):
            logger.info(f"🔍 Processing {i}/{len(urls)}: {url}")

            try:
                property_data = self.scrape_property_detail(url)
                if property_data:
                    properties.append(property_data)
                    logger.success(f"✓ {property_data.get('title', 'Unknown')}")

                    # DB保存
                    if save_to_db:
                        self.save_to_database(property_data)

                self.url_queue.mark_completed(url)
            except Exception as e:
                logger.error(f"✗ Failed: {e}")
                self.url_queue.mark_completed(url)

            if i < len(urls):
                self.rate_limiter.wait()

        return properties

    @retry(max_attempts=3)
    def scrape_property_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """物件詳細ページをスクレイピング"""
        html = self.get_page_source(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # 基本データ作成（共通ライブラリ使用）
        property_data = create_property_base_data(url, "homes")

        # タイトル
        title_elem = soup.select_one(self.selectors["detail_title"])
        if title_elem:
            property_data["title"] = title_elem.get_text(strip=True)

        # 価格
        price_data = self._extract_price(soup)
        property_data.update(price_data)

        # テーブルデータ（汎用的に）
        table_data = self._extract_table_data_generic(soup)
        property_data.update(table_data)

        # 元請会社情報
        contractor_info = self._extract_contractor_info(soup)
        property_data.update(contractor_info)

        # 物件タイプ（共通ライブラリ使用）
        property_data["property_type"] = determine_property_type(
            url, property_data.get("title", "")
        )

        # listing_id
        property_data["listing_id"] = extract_listing_id(url, "homes")

        return property_data

    def _extract_price(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """価格抽出（汎用化）"""
        for elem in soup.find_all(["td", "span", "div"]):
            text = elem.get_text(strip=True)
            if "万円" in text and text[0].isdigit():
                match = re.search(r"(\d{1,5}(?:,\d{3})*(?:\.\d+)?)\s*万円", text)
                if match:
                    return {
                        "price_raw": match.group(0),
                        "price": parse_sale_price(match.group(0)),
                    }
        return {}

    def _extract_table_data_generic(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """テーブルデータ抽出（汎用化）"""
        result = {}

        for tr in soup.find_all("tr"):
            th = tr.find("th")
            td = tr.find("td")
            if th and td:
                header = th.get_text(strip=True)
                value = td.get_text(strip=True)

                # マッピングに基づいて処理
                for key_pattern, (field_name, processor) in self.table_mapping.items():
                    if key_pattern in header:
                        result[field_name] = processor(value)
                        break

        return result

    def _extract_contractor_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """元請会社情報抽出"""
        contractor_info = {}

        # 会社名
        company_elem = soup.select_one(self.selectors["company_name"])
        if company_elem:
            contractor_info["contractor_company_name"] = company_elem.get_text(
                strip=True
            )

        # 電話番号
        phone_elem = soup.select_one(self.selectors["company_phone"])
        if phone_elem:
            phone_text = phone_elem.get_text(strip=True)
            contractor_info["contractor_phone"] = clean_phone_number(phone_text)

        return contractor_info

    def _find_next_page(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """次ページ検索"""
        for selector in self.selectors["next_page"]:
            next_elem = soup.select_one(selector)
            if next_elem and next_elem.get("href"):
                return urljoin(current_url, next_elem["href"])
        return None

    def save_to_database(self, property_data: Dict[str, Any]):
        """物件データをDBに保存"""
        try:
            query = """
            INSERT INTO properties (
                homes_record_id,
                building_property_name,
                price,
                address_name,
                contractor_company_name,
                contractor_phone,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (homes_record_id) DO UPDATE SET
                building_property_name = EXCLUDED.building_property_name,
                price = EXCLUDED.price,
                updated_at = NOW()
            """

            params = (
                property_data.get("listing_id"),
                property_data.get("title"),
                property_data.get("price"),
                property_data.get("address"),
                property_data.get("contractor_company_name"),
                property_data.get("contractor_phone"),
            )

            READatabase.execute_query(query, params)
            logger.success(f"✅ DB保存完了: {property_data.get('title')}")

        except Exception as e:
            logger.error(f"❌ DB保存エラー: {e}")

    def get_queue_stats(self) -> Dict[str, int]:
        """統計情報取得"""
        return self.url_queue.get_stats()

    def reset_queue(self):
        """キューリセット"""
        self.url_queue.reset()

    # 互換性メソッド
    def scrape_listing_page(self, url: str) -> List[Dict[str, Any]]:
        self.collect_property_urls(url, max_pages=1)
        return []

    def scrape_detail_page(self, url: str) -> Optional[Dict[str, Any]]:
        return self.scrape_property_detail(url)


# テスト実行
if __name__ == "__main__":
    logger.info("🚀 [Homes] Test execution start")

    scraper = HomesPropertyScraper()

    try:
        # URL収集テスト
        test_url = "https://www.homes.co.jp/kodate/hokkaido/list/"
        collected = scraper.collect_property_urls(test_url, max_pages=2)
        logger.info(f"✅ Collected {collected} URLs")

        # バッチ処理テスト（DB保存付き）
        properties = scraper.process_batch(batch_size=3, save_to_db=True)

        if properties:
            logger.info(f"✅ Scraped {len(properties)} properties")
            for prop in properties[:2]:  # 最初の2件だけ表示
                logger.info(f"  - {prop.get('title')}")
                logger.info(f"    💰 {prop.get('price_raw')}")
                logger.info(f"    🏢 {prop.get('contractor_company_name', 'N/A')}")

        # 統計
        stats = scraper.get_queue_stats()
        logger.info(f"📊 Stats: {stats}")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    finally:
        scraper.close()
        logger.info("🏁 Test completed")
