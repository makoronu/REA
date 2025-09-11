"""
基底スクレイパークラス
全スクレイパーの共通機能を提供
"""
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.config.database import db_manager
from src.config.settings import settings
from src.utils.selenium_manager import SeleniumManager


class BaseScraper(ABC):
    """全スクレイパーの基底クラス"""

    def __init__(self, site_name: str, base_url: str, login_required: bool = False):
        """
        Args:
            site_name: サイト名（例: 'homes', 'suumo'）
            base_url: ベースURL（例: 'https://www.homes.co.jp'）
            login_required: ログインが必要かどうか
        """
        self.site_name = site_name
        self.base_url = base_url
        self.login_required = login_required

        # Selenium Manager
        self.selenium_manager = SeleniumManager()
        self.driver = None

        # リクエストセッション（軽量な取得用）
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )

        # 統計情報
        self.stats = {
            "pages_scraped": 0,
            "properties_found": 0,
            "errors": 0,
            "start_time": datetime.now(),
        }

        logger.info(f"Initialized {self.site_name} scraper")

    def get_driver(self) -> webdriver.Chrome:
        """Seleniumドライバーを取得（遅延初期化）"""
        if not self.driver:
            self.driver = self.selenium_manager.create_driver()
        return self.driver

    def get_page_source(self, url: str, use_selenium: bool = True) -> Optional[str]:
        """ページのHTMLを取得"""
        try:
            if use_selenium:
                driver = self.get_driver()
                driver.get(url)

                # ページ読み込み待機
                WebDriverWait(driver, settings.DEFAULT_TIMEOUT).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                # 動的コンテンツの読み込み待機
                time.sleep(settings.RATE_LIMIT_DELAY)

                return driver.page_source
            else:
                # 軽量な取得（静的ページ用）
                response = self.session.get(url, timeout=settings.DEFAULT_TIMEOUT)
                response.raise_for_status()
                return response.text

        except TimeoutException:
            logger.error(f"Timeout loading page: {url}")
            self.stats["errors"] += 1
            return None
        except Exception as e:
            logger.error(f"Error loading page {url}: {e}")
            self.stats["errors"] += 1
            return None

    def wait_for_element(
        self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = None
    ) -> Optional[Any]:
        """要素の出現を待機"""
        if not self.driver:
            return None

        timeout = timeout or settings.DEFAULT_TIMEOUT
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            logger.debug(f"Element not found: {selector}")
            return None

    def save_properties(self, properties: List[Dict[str, Any]]) -> int:
        """物件データを保存"""
        saved_count = 0

        for property_data in properties:
            try:
                # データ検証
                if self.validate_property_data(property_data):
                    property_id = db_manager.save_property(property_data)
                    if property_id:
                        saved_count += 1
                        logger.debug(
                            f"Saved property: {property_data.get('title', 'No title')}"
                        )
                else:
                    logger.warning(f"Invalid property data: {property_data}")

            except Exception as e:
                logger.error(f"Error saving property: {e}")
                continue

        logger.info(f"Saved {saved_count}/{len(properties)} properties")
        return saved_count

    def validate_property_data(self, data: Dict[str, Any]) -> bool:
        """売買物件データの妥当性を検証"""
        # 必須フィールド
        required_fields = ["title", "price", "source_url", "source_site"]
        for field in required_fields:
            if field not in data or not data[field]:
                logger.debug(f"Missing required field: {field}")
                return False

        # 価格の妥当性（売買: 100万円〜10億円）
        price = data.get("price", 0)
        if (
            not isinstance(price, (int, float))
            or price < 1000000
            or price > 10000000000
        ):
            logger.debug(f"Invalid sale price: {price}")
            return False

        # 取引種別
        if data.get("transaction_type") != "売買":
            logger.debug(f"Not a sale property: {data.get('transaction_type')}")
            return False

        # URLの妥当性
        url = data.get("source_url", "")
        if not url.startswith("http"):
            logger.debug(f"Invalid URL: {url}")
            return False

        return True

    def extract_text(self, element: Any, default: str = "") -> str:
        """要素からテキストを安全に抽出"""
        try:
            if hasattr(element, "get_text"):  # BeautifulSoup
                return element.get_text(strip=True) or default
            elif hasattr(element, "text"):  # Selenium
                return element.text.strip() or default
            else:
                return str(element).strip() or default
        except Exception:
            return default

    def close(self):
        """リソースをクリーンアップ"""
        if self.driver:
            self.selenium_manager.quit_driver(self.driver)
            self.driver = None

        # 統計情報を出力
        duration = (datetime.now() - self.stats["start_time"]).total_seconds()
        logger.info(
            f"""
        Scraping completed for {self.site_name}:
        - Duration: {duration:.1f} seconds
        - Pages scraped: {self.stats['pages_scraped']}
        - Properties found: {self.stats['properties_found']}
        - Errors: {self.stats['errors']}
        """
        )

    @abstractmethod
    def scrape_listing_page(self, url: str) -> List[Dict[str, Any]]:
        """物件一覧ページをスクレイピング（各サイトで実装）"""
        pass

    @abstractmethod
    def scrape_detail_page(self, url: str) -> Optional[Dict[str, Any]]:
        """物件詳細ページをスクレイピング（各サイトで実装）"""
        pass

    def run(self, urls: List[str], max_pages: int = 10) -> List[Dict[str, Any]]:
        """スクレイピングを実行"""
        all_properties = []

        try:
            for i, url in enumerate(urls[:max_pages]):
                logger.info(f"Processing page {i+1}/{min(len(urls), max_pages)}: {url}")

                properties = self.scrape_listing_page(url)
                if properties:
                    all_properties.extend(properties)
                    self.stats["properties_found"] += len(properties)

                self.stats["pages_scraped"] += 1

                # レート制限
                if i < len(urls) - 1:
                    time.sleep(settings.RATE_LIMIT_DELAY)

            # データベースに保存
            if all_properties:
                self.save_properties(all_properties)

        finally:
            self.close()

        return all_properties


# 売買物件用のユーティリティ関数
def parse_japanese_number(text: str) -> Optional[float]:
    """日本語の数値表記をパース（億、万など）"""
    import re

    # 億万円のパターン
    pattern = r"(\d+)億(\d+)万円"
    match = re.search(pattern, text)
    if match:
        return float(match.group(1)) * 100000000 + float(match.group(2)) * 10000

    # 億円のパターン
    pattern = r"(\d+)億円"
    match = re.search(pattern, text)
    if match:
        return float(match.group(1)) * 100000000

    # 万円のパターン
    pattern = r"(\d+(?:,\d+)*)万円"
    match = re.search(pattern, text)
    if match:
        num_str = match.group(1).replace(",", "")
        return float(num_str) * 10000

    return None


def normalize_address(address: str) -> str:
    """住所を正規化"""
    import re

    # 全角数字を半角に
    trans_table = str.maketrans("０１２３４５６７８９", "0123456789")
    address = address.translate(trans_table)

    # 全角ハイフンを半角に
    address = address.replace("－", "-").replace("ー", "-")

    # 余分な空白を削除
    address = re.sub(r"\s+", " ", address).strip()

    return address
