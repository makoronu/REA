"""
Selenium WebDriver管理モジュール
耐障害性・回避策強化版
"""
import random
import time
from pathlib import Path
from typing import List, Optional

import undetected_chromedriver as uc
from fake_useragent import UserAgent
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.config.settings import settings


class SeleniumManager:
    """Selenium WebDriver管理クラス（耐障害性強化版）"""

    def __init__(self):
        self.drivers = []
        self.ua = UserAgent()
        self.proxy_list = self._load_proxies()
        self.current_proxy_index = 0
        self.error_count = 0
        self.max_errors = 10

    def _load_proxies(self) -> List[str]:
        """プロキシリストを読み込み"""
        proxy_file = Path("data/proxies.txt")
        if proxy_file.exists():
            return proxy_file.read_text().strip().split("\n")
        return []

    def _get_chrome_options(self) -> Options:
        """Chrome オプション設定（Bot検出回避）"""
        options = uc.ChromeOptions()

        # 基本的なBot検出回避設定
        options.add_argument("--disable-blink-features=AutomationControlled")
        # undetected-chromedriverではexcludeSwitchesは自動設定されるのでコメントアウト
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)

        # ランダムなユーザーエージェント
        options.add_argument(f"user-agent={self.ua.random}")

        # ヘッドレスモード（必要に応じて）
        if settings.HEADLESS_MODE:
            options.add_argument("--headless=new")  # 新しいヘッドレスモード

        # ウィンドウサイズ（ランダム化）
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f"--window-size={width},{height}")

        # その他の設定
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-software-rasterizer")

        # 画像無効化（高速化）
        if getattr(settings, "DISABLE_IMAGES", True):
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)

        # プロキシ設定（利用可能な場合）
        if self.proxy_list and getattr(settings, "USE_PROXY", False):
            proxy = self.proxy_list[self.current_proxy_index]
            options.add_argument(f"--proxy-server={proxy}")
            self.current_proxy_index = (self.current_proxy_index + 1) % len(
                self.proxy_list
            )

        # WebRTC無効化（IPリーク防止）
        options.add_experimental_option(
            "prefs",
            {
                "webrtc.ip_handling_policy": "disable_non_proxied_udp",
                "webrtc.multiple_routes_enabled": False,
                "webrtc.nonproxied_udp_enabled": False,
            },
        )

        return options

    def create_driver(self, retry_count: int = 3) -> Optional[webdriver.Chrome]:
        """Chrome WebDriverを作成（リトライ機能付き）"""
        for attempt in range(retry_count):
            try:
                # undetected-chromedriverを使用
                driver = uc.Chrome(
                    options=self._get_chrome_options(), version_main=None  # 自動でバージョン検出
                )

                # JavaScriptでNavigator.webdriverを削除
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )

                # タイムアウト設定
                driver.set_page_load_timeout(30)
                driver.implicitly_wait(10)

                self.drivers.append(driver)
                logger.info(
                    f"Chrome driver created successfully. Total active drivers: {len(self.drivers)}"
                )

                # 初期待機（人間らしく）
                time.sleep(random.uniform(1, 3))

                return driver

            except Exception as e:
                logger.error(
                    f"Failed to create driver (attempt {attempt + 1}/{retry_count}): {e}"
                )
                if attempt < retry_count - 1:
                    time.sleep(5)
                else:
                    self.error_count += 1
                    if self.error_count >= self.max_errors:
                        logger.critical(
                            "Too many driver creation errors. Possible IP ban."
                        )

        return None

    def wait_for_element(
        self,
        driver: webdriver.Chrome,
        selector: str,
        timeout: int = 10,
        by: By = By.CSS_SELECTOR,
    ) -> Optional:
        """要素の待機（複数の方法を試す）"""
        strategies = [
            (By.CSS_SELECTOR, selector),
            (
                By.XPATH,
                f"//*[contains(@class, '{selector}')]" if "." in selector else selector,
            ),
            (
                By.CLASS_NAME,
                selector.replace(".", "") if selector.startswith(".") else selector,
            ),
        ]

        for by_method, locator in strategies:
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by_method, locator))
                )
                return element
            except TimeoutException:
                continue

        return None

    def safe_get(
        self, driver: webdriver.Chrome, url: str, max_retries: int = 3
    ) -> bool:
        """安全なページ取得（リトライ・エラーハンドリング付き）"""
        for attempt in range(max_retries):
            try:
                # 人間らしい待機
                if attempt > 0:
                    wait_time = random.uniform(5, 15) * attempt
                    logger.info(f"Waiting {wait_time:.1f}s before retry...")
                    time.sleep(wait_time)

                driver.get(url)

                # ページ読み込み待機
                time.sleep(random.uniform(2, 5))

                # Cloudflareチェック
                if self._check_cloudflare(driver):
                    logger.warning("Cloudflare detected, waiting...")
                    time.sleep(10)
                    # 手動で解決が必要な場合もある

                # 成功
                self.error_count = 0  # エラーカウントリセット
                return True

            except TimeoutException:
                logger.warning(f"Timeout loading {url} (attempt {attempt + 1})")
            except WebDriverException as e:
                logger.error(f"WebDriver error: {e}")
                if "net::ERR_CONNECTION_REFUSED" in str(e):
                    logger.error("Connection refused. Possible IP ban.")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error loading {url}: {e}")

        self.error_count += 1
        return False

    def _check_cloudflare(self, driver: webdriver.Chrome) -> bool:
        """Cloudflare検出"""
        indicators = [
            "Checking your browser",
            "Please wait",
            "DDoS protection by Cloudflare",
            "cf-browser-verification",
        ]

        page_source = driver.page_source.lower()
        for indicator in indicators:
            if indicator.lower() in page_source:
                return True

        # Cloudflare特有の要素をチェック
        try:
            driver.find_element(By.CLASS_NAME, "cf-browser-verification")
            return True
        except:
            pass

        return False

    def random_scroll(self, driver: webdriver.Chrome):
        """ランダムスクロール（人間らしい動作）"""
        scroll_pause_time = random.uniform(0.5, 2)

        # ページの高さを取得
        last_height = driver.execute_script("return document.body.scrollHeight")

        # ランダムにスクロール
        for i in range(random.randint(3, 7)):
            # ランダムな位置にスクロール
            scroll_to = random.randint(100, last_height)
            driver.execute_script(f"window.scrollTo(0, {scroll_to});")
            time.sleep(scroll_pause_time)

    def take_screenshot(self, driver: webdriver.Chrome, filename: str):
        """スクリーンショット保存（デバッグ用）"""
        try:
            screenshot_dir = Path("data/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            filepath = screenshot_dir / filename
            driver.save_screenshot(str(filepath))
            logger.info(f"Screenshot saved: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")

    def quit_driver(self, driver: webdriver.Chrome):
        """ドライバーを安全に終了"""
        try:
            if driver in self.drivers:
                self.drivers.remove(driver)
            driver.quit()
            logger.info(
                f"Chrome driver closed. Remaining active drivers: {len(self.drivers)}"
            )
        except Exception as e:
            logger.error(f"Error closing driver: {e}")

    def quit_all_drivers(self):
        """すべてのドライバーを終了"""
        for driver in self.drivers[:]:
            self.quit_driver(driver)
        logger.info("All drivers closed")

    def get_driver_stats(self) -> dict:
        """ドライバーの統計情報"""
        return {
            "active_drivers": len(self.drivers),
            "error_count": self.error_count,
            "proxy_count": len(self.proxy_list),
            "current_proxy": self.proxy_list[self.current_proxy_index]
            if self.proxy_list
            else None,
        }


# 使用例
if __name__ == "__main__":
    manager = SeleniumManager()

    # Bot検出回避テスト
    driver = manager.create_driver()
    if driver:
        # テストサイトでBot検出をチェック
        test_urls = [
            "https://bot.sannysoft.com/",  # Bot検出テスト
            "https://www.homes.co.jp/kodate/hokkaido/list/",
        ]

        for url in test_urls:
            logger.info(f"Testing: {url}")
            if manager.safe_get(driver, url):
                # 人間らしい動作
                manager.random_scroll(driver)
                time.sleep(3)

                # スクリーンショット
                manager.take_screenshot(driver, f"test_{url.split('/')[2]}.png")

        manager.quit_driver(driver)
