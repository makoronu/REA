"""
ホームズ不動産売買物件スクレイパー
段階的処理・レート制限対応版
"""
import json
import pickle
import random
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from loguru import logger
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from src.config.database import db_manager
from src.scrapers.base.base_scraper import BaseScraper
from src.utils.decorators import handle_errors, measure_time, retry


class URLQueue:
    """URL収集と管理を行うクラス"""

    def __init__(self, cache_dir: str = "data/url_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.queue_file = self.cache_dir / "homes_url_queue.pkl"
        self.completed_file = self.cache_dir / "homes_completed_urls.pkl"
        self.queue = []
        self.completed = set()
        self._load_state()

    def _load_state(self):
        """保存された状態を読み込む"""
        if self.queue_file.exists():
            with open(self.queue_file, "rb") as f:
                self.queue = pickle.load(f)
            logger.info(f"Loaded {len(self.queue)} URLs from queue")

        if self.completed_file.exists():
            with open(self.completed_file, "rb") as f:
                self.completed = pickle.load(f)
            logger.info(f"Loaded {len(self.completed)} completed URLs")

    def save_state(self):
        """現在の状態を保存"""
        with open(self.queue_file, "wb") as f:
            pickle.dump(self.queue, f)

        with open(self.completed_file, "wb") as f:
            pickle.dump(self.completed, f)

        logger.info(
            f"Saved queue state: {len(self.queue)} pending, {len(self.completed)} completed"
        )

    def add_urls(self, urls: List[str]):
        """URLをキューに追加"""
        new_urls = []
        for url in urls:
            if url not in self.completed and url not in self.queue:
                new_urls.append(url)
                self.queue.append(url)

        logger.info(f"Added {len(new_urls)} new URLs to queue")
        self.save_state()

    def get_next_batch(self, batch_size: int = 10) -> List[str]:
        """次のバッチを取得"""
        batch = self.queue[:batch_size]
        self.queue = self.queue[batch_size:]
        return batch

    def mark_completed(self, url: str):
        """URLを完了済みとしてマーク"""
        self.completed.add(url)
        if url in self.queue:
            self.queue.remove(url)
        self.save_state()

    def get_stats(self) -> Dict[str, int]:
        """統計情報を取得"""
        return {
            "pending": len(self.queue),
            "completed": len(self.completed),
            "total": len(self.queue) + len(self.completed),
        }


class HomesPropertyScraper(BaseScraper):
    """ホームズ売買物件専用スクレイパー（段階処理版）"""

    def __init__(self):
        super().__init__(
            site_name="homes", base_url="https://www.homes.co.jp", login_required=False
        )

        # URL管理
        self.url_queue = URLQueue()

        # レート制限設定
        self.rate_limit = {
            "min_delay": 3,  # 最小待機時間（秒）
            "max_delay": 8,  # 最大待機時間（秒）
            "batch_size": 10,  # 1バッチあたりの処理数
            "batch_interval": 300,  # バッチ間隔（秒）
        }

        # セレクタ定義
        self.selectors = {
            # 一覧ページ
            "property_items": ".moduleInner.prg-kksSictClickInfo",
            "property_link": 'a[href*="/kodate/b-"], a[href*="/mansion/b-"], a[href*="/tochi/b-"]',
            "next_page": 'a[data-page]:contains("次へ"), .pagination__next a',
            "pagination": ".pagination",
            # 詳細ページ（修正版）
            "detail_title": "h1, .bukkenName",
            "price": 'table td:contains("万円"), .num:contains("万円")',
            "address": "h1, title",  # タイトルから住所を抽出
            "land_area": 'th:contains("土地面積") + td',
            "building_area": 'th:contains("建物面積") + td',
            "floor_plan": 'th:contains("間取り") + td',
            "construction_year": 'th:contains("築年月") + td',
            "structure": 'th:contains("構造") + td',
            # 元請会社情報（修正版）
            "company_section": ".shopName, .company-info, .shopInfo",
            "company_name": ".shopName",
            "company_phone": ".freeCall, span.u-text-2xl",
            "company_license": 'dt:contains("免許番号") + dd',
            "company_address": 'dt:contains("所在地") + dd',
            "contact_person": ".staffName, .staff-name",
        }

    def collect_property_urls(self, base_url: str, max_pages: int = 50) -> int:
        """
        Step 1: 物件URLを収集してキューに保存

        Args:
            base_url: 一覧ページのURL
            max_pages: 最大ページ数

        Returns:
            収集したURL数
        """
        logger.info(f"Starting URL collection from: {base_url}")
        collected_urls = []
        current_url = base_url
        page_num = 1

        while page_num <= max_pages:
            logger.info(f"Collecting URLs from page {page_num}: {current_url}")

            try:
                html = self.get_page_source(current_url)
                if not html:
                    break

                soup = BeautifulSoup(html, "html.parser")

                # 物件リンクを収集
                property_links = soup.select(self.selectors["property_link"])
                page_urls = []

                for link in property_links:
                    href = link.get("href")
                    if href:
                        full_url = urljoin(self.base_url, href)
                        page_urls.append(full_url)

                collected_urls.extend(page_urls)
                logger.info(f"Found {len(page_urls)} properties on page {page_num}")

                # 次ページのリンクを探す
                next_link = self._find_next_page(soup, current_url)
                if not next_link:
                    logger.info("No more pages found")
                    break

                current_url = next_link
                page_num += 1

                # レート制限
                delay = random.uniform(
                    self.rate_limit["min_delay"], self.rate_limit["max_delay"]
                )
                time.sleep(delay)

            except Exception as e:
                logger.error(f"Error on page {page_num}: {e}")
                break

        # URLをキューに追加
        self.url_queue.add_urls(collected_urls)

        stats = self.url_queue.get_stats()
        logger.info(
            f"URL collection completed. Total: {stats['total']}, New: {len(collected_urls)}"
        )

        return len(collected_urls)

    def process_batch(self, batch_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Step 2: キューから指定数の物件を処理

        Args:
            batch_size: 処理する物件数（Noneの場合はデフォルト値）

        Returns:
            取得した物件情報のリスト
        """
        if batch_size is None:
            batch_size = self.rate_limit["batch_size"]

        stats = self.url_queue.get_stats()
        logger.info(
            f"Processing batch: {batch_size} properties (Pending: {stats['pending']})"
        )

        # バッチを取得
        urls = self.url_queue.get_next_batch(batch_size)
        if not urls:
            logger.info("No URLs in queue")
            return []

        properties = []

        for i, url in enumerate(urls, 1):
            logger.info(f"Processing {i}/{len(urls)}: {url}")

            try:
                # 詳細ページをスクレイピング
                property_data = self.scrape_property_detail(url)

                if property_data:
                    properties.append(property_data)
                    logger.success(
                        f"✓ Successfully scraped: {property_data.get('title', 'Unknown')}"
                    )

                    # データベースに保存（オプション）
                    if hasattr(self, "save_to_db") and self.save_to_db:
                        self._save_property(property_data)

                # 完了済みとしてマーク
                self.url_queue.mark_completed(url)

            except Exception as e:
                logger.error(f"✗ Failed to scrape {url}: {e}")
                # エラーが発生してもURLは完了済みとしてマーク（無限ループ防止）
                self.url_queue.mark_completed(url)

            # レート制限（最後の1件以外）
            if i < len(urls):
                delay = random.uniform(
                    self.rate_limit["min_delay"], self.rate_limit["max_delay"]
                )
                time.sleep(delay)

        logger.info(f"Batch completed. Scraped: {len(properties)}/{len(urls)}")
        return properties

    def process_all_remaining(
        self, batch_size: int = 10, batch_interval: int = 300
    ) -> int:
        """
        Step 3: 残りのURLをすべて処理（時間をかけて）

        Args:
            batch_size: 1バッチあたりの処理数
            batch_interval: バッチ間の待機時間（秒）

        Returns:
            処理した総物件数
        """
        total_processed = 0
        batch_num = 1

        while True:
            stats = self.url_queue.get_stats()
            if stats["pending"] == 0:
                logger.info("All URLs processed!")
                break

            logger.info(f"Starting batch {batch_num} (Remaining: {stats['pending']})")

            # バッチを処理
            properties = self.process_batch(batch_size)
            total_processed += len(properties)

            # 次のバッチまで待機
            if stats["pending"] > 0:
                logger.info(f"Waiting {batch_interval} seconds before next batch...")
                time.sleep(batch_interval)

            batch_num += 1

        return total_processed

    @retry(max_attempts=3)
    def scrape_property_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """物件詳細ページをスクレイピング"""
        logger.debug(f"Scraping detail page: {url}")

        html = self.get_page_source(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # 基本情報を抽出
        property_data = {
            "source_site": "homes",
            "source_url": url,
            "listing_id": self._extract_listing_id(url),
            "transaction_type": "売買",
            "scraped_at": datetime.now().isoformat(),
        }

        # タイトル（修正版）
        title_elem = soup.find("h1", class_="name")
        if not title_elem:
            title_elem = soup.find("h1")
        if title_elem:
            property_data["title"] = title_elem.get_text(strip=True)

        # 価格（テーブルから直接取得）
        price_found = False
        for td in soup.find_all("td"):
            text = td.get_text(strip=True)
            if "万円" in text and text[0].isdigit():
                # 価格だけを抽出
                import re

                price_match = re.search(r"(\d{1,5}(?:,\d{3})*(?:\.\d+)?)\s*万円", text)
                if price_match:
                    property_data["price_raw"] = price_match.group(0)
                    property_data["price"] = self._parse_sale_price(
                        price_match.group(0)
                    )
                    price_found = True
                    break

        # 住所（dlタグから）
        for dl in soup.find_all("dl"):
            dt = dl.find("dt")
            dd = dl.find("dd")
            if dt and dd and "所在地" in dt.get_text():
                address_text = dd.get_text(strip=True)
                # 「地図を見る」などを削除
                address_text = re.sub(r"(地図を見る|無料|詳細な所在地を教えてほしい).*", "", address_text)
                property_data["address"] = self._normalize_address(address_text.strip())
                break

        # 土地面積（テーブルから）
        for tr in soup.find_all("tr"):
            th = tr.find("th")
            td = tr.find("td")
            if th and td:
                header = th.get_text(strip=True)
                value = td.get_text(strip=True)

                if "土地面積" in header:
                    property_data["land_area"] = self._parse_area(value)
                elif "建物面積" in header:
                    property_data["building_area"] = self._parse_area(value)
                elif "間取り" in header:
                    property_data["floor_plan"] = value
                elif "築年月" in header:
                    property_data["construction_year"] = self._parse_construction_year(
                        value
                    )
                elif "構造" in header:
                    property_data["structure"] = value

        # 元請会社情報（修正版）
        # 会社名
        company_elem = soup.find("p", class_="shopName")
        if company_elem:
            property_data["contractor_company_name"] = company_elem.get_text(strip=True)

        # 電話番号
        phone_elem = soup.find("span", class_="freeCall")
        if phone_elem:
            phone_text = phone_elem.get_text(strip=True)
            cleaned_phone = re.sub(r"[^\d-]", "", phone_text)
            if re.match(r"^\d{2,4}-\d{2,4}-\d{3,4}$", cleaned_phone):
                property_data["contractor_phone"] = cleaned_phone

        # 物件タイプを判定
        property_data["property_type"] = self._determine_property_type(
            url, property_data
        )

        return property_data

    def _find_next_page(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """次ページのURLを探す"""
        # 複数のセレクタパターンを試す
        next_selectors = [
            'a:contains("次へ")',
            "a.next",
            ".pagination__next a",
            'a[rel="next"]',
        ]

        for selector in next_selectors:
            next_elem = soup.select_one(selector)
            if next_elem and next_elem.get("href"):
                return urljoin(current_url, next_elem["href"])

        # data-page属性で次のページ番号を探す
        current_page = 1
        page_match = re.search(r"page=(\d+)", current_url)
        if page_match:
            current_page = int(page_match.group(1))

        next_page_elem = soup.select_one(f'a[data-page="{current_page + 1}"]')
        if next_page_elem and next_page_elem.get("href"):
            return urljoin(current_url, next_page_elem["href"])

        return None

    def _extract_contractor_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """元請会社情報を詳細ページから抽出"""
        contractor_info = {}

        # 会社情報セクションを探す（複数のセレクタを試す）
        company_section = None
        for selector in self.selectors["company_section"].split(", "):
            company_section = soup.select_one(selector)
            if company_section:
                break

        if company_section:
            # 会社名
            for selector in self.selectors["company_name"].split(", "):
                name_elem = company_section.select_one(selector)
                if name_elem:
                    contractor_info["contractor_company_name"] = name_elem.get_text(
                        strip=True
                    )
                    break

            # 電話番号
            for selector in self.selectors["company_phone"].split(", "):
                phone_elem = company_section.select_one(selector)
                if phone_elem:
                    phone_text = phone_elem.get_text(strip=True)
                    cleaned_phone = re.sub(r"[^\d-]", "", phone_text)
                    if re.match(r"^\d{2,4}-\d{2,4}-\d{3,4}$", cleaned_phone):
                        contractor_info["contractor_phone"] = cleaned_phone
                        break

            # 免許番号
            license_elem = company_section.select_one(self.selectors["company_license"])
            if license_elem:
                contractor_info["contractor_license_number"] = license_elem.get_text(
                    strip=True
                )

            # 会社住所
            address_elem = company_section.select_one(self.selectors["company_address"])
            if address_elem:
                contractor_info["contractor_address"] = self._normalize_address(
                    address_elem.get_text(strip=True)
                )

        # 会社情報が見つからない場合は、ページ全体から探す
        if not contractor_info.get("contractor_company_name"):
            # 会社名パターンで検索
            company_pattern = re.compile(r"((?:株式会社|有限会社|合同会社)[^。、\s]{2,20})")
            company_text = soup.get_text()
            matches = company_pattern.findall(company_text)
            if matches:
                # 最初に見つかった会社名を使用
                contractor_info["contractor_company_name"] = matches[0]

        return contractor_info

    def _parse_sale_price(self, price_text: str) -> Optional[float]:
        """売買価格をパース"""
        # カンマを削除
        price_text = price_text.replace(",", "")

        # 価格パターン
        patterns = [
            (
                r"(\d+)億(\d+)万円",
                lambda m: float(m.group(1)) * 100000000 + float(m.group(2)) * 10000,
            ),
            (r"(\d+)億円", lambda m: float(m.group(1)) * 100000000),
            (r"(\d+)万円", lambda m: float(m.group(1)) * 10000),
        ]

        for pattern, converter in patterns:
            match = re.search(pattern, price_text)
            if match:
                return converter(match)

        return None

    def _parse_area(self, area_text: str) -> Optional[float]:
        """面積をパース"""
        match = re.search(r"(\d+(?:\.\d+)?)", area_text)
        if match:
            return float(match.group(1))
        return None

    def _parse_construction_year(self, text: str) -> Optional[int]:
        """築年月から年を抽出"""
        # 西暦
        match = re.search(r"(\d{4})年", text)
        if match:
            return int(match.group(1))

        # 和暦変換
        wareki_patterns = [
            ("令和", r"令和(\d+)年", 2018),
            ("平成", r"平成(\d+)年", 1988),
            ("昭和", r"昭和(\d+)年", 1925),
        ]

        for era_name, pattern, base_year in wareki_patterns:
            if era_name in text:
                match = re.search(pattern, text)
                if match:
                    return base_year + int(match.group(1))

        return None

    def _normalize_address(self, address: str) -> str:
        """住所を正規化"""
        # 全角数字を半角に変換
        address = address.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        # 余分な空白を削除
        address = re.sub(r"\s+", " ", address).strip()
        # 改行を削除
        address = address.replace("\n", " ").replace("\r", "")
        return address

    def _extract_listing_id(self, url: str) -> Optional[str]:
        """URLから物件IDを抽出"""
        match = re.search(r"/b-(\d+)/", url)
        if match:
            return f"homes_{match.group(1)}"
        return None

    def _determine_property_type(self, url: str, property_data: Dict[str, Any]) -> str:
        """物件タイプを判定"""
        if "/kodate/" in url:
            return "戸建て"
        elif "/mansion/" in url:
            return "マンション"
        elif "/tochi/" in url:
            return "土地"
        else:
            # タイトルから判定
            title = property_data.get("title", "").lower()
            if "マンション" in title:
                return "マンション"
            elif "土地" in title:
                return "土地"
            else:
                return "戸建て"

    def _save_property(self, property_data: Dict[str, Any]):
        """物件データをデータベースに保存"""
        try:
            db_manager.save_property(property_data)
            logger.debug(f"Saved property: {property_data.get('listing_id')}")
        except Exception as e:
            logger.error(f"Failed to save property: {e}")

    def get_queue_stats(self) -> Dict[str, int]:
        """キューの統計情報を取得"""
        return self.url_queue.get_stats()

    def reset_queue(self):
        """キューをリセット（テスト用）"""
        self.url_queue.queue = []
        self.url_queue.completed = set()
        self.url_queue.save_state()
        logger.info("Queue reset")

    # 抽象メソッドの実装（base_scraperとの互換性のため）
    def scrape_listing_page(self, url: str) -> List[Dict[str, Any]]:
        """物件一覧ページをスクレイピング（従来の互換性メソッド）"""
        logger.info("scrape_listing_page called - using collect_property_urls instead")
        # URL収集だけ行う
        self.collect_property_urls(url, max_pages=1)
        # 空のリストを返す（詳細は別途取得するため）
        return []

    def scrape_detail_page(self, url: str) -> Optional[Dict[str, Any]]:
        """物件詳細ページをスクレイピング（従来の互換性メソッド）"""
        return self.scrape_property_detail(url)


# テスト実行
if __name__ == "__main__":
    scraper = HomesPropertyScraper()

    # Step 1: URL収集
    test_url = "https://www.homes.co.jp/kodate/hokkaido/list/"
    collected = scraper.collect_property_urls(test_url, max_pages=3)
    logger.info(f"Collected {collected} URLs")

    # Step 2: バッチ処理
    properties = scraper.process_batch(batch_size=3)

    if properties:
        logger.info(f"✓ Scraped {len(properties)} properties")
        for prop in properties:
            logger.info(f"  - {prop.get('title')}: {prop.get('price_raw')}")
            logger.info(
                f"    Company: {prop.get('contractor_company_name', 'Not found')}"
            )

    # 統計情報
    stats = scraper.get_queue_stats()
    logger.info(f"Queue stats: {stats}")

    scraper.close()
