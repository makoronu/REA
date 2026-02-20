"""
REAスクレイピング共通処理
URL管理、データ抽出、エラーハンドリング等の共通機能
"""

import pickle
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from loguru import logger


class URLQueue:
    """
    URL収集と管理を行う汎用クラス
    複数のスクレイピングサイトで共通利用可能
    """

    def __init__(self, site_name: str, cache_dir: str = "data/url_cache"):
        """
        Args:
            site_name: サイト名（homes, suumo等）
            cache_dir: キャッシュディレクトリ
        """
        self.site_name = site_name
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # サイト別のキャッシュファイル
        self.queue_file = self.cache_dir / f"{site_name}_url_queue.pkl"
        self.completed_file = self.cache_dir / f"{site_name}_completed_urls.pkl"

        self.queue = []
        self.completed = set()
        self._load_state()

    def _load_state(self):
        """保存された状態を読み込む"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, "rb") as f:
                    self.queue = pickle.load(f)
                logger.info(
                    f"[{self.site_name}] Loaded {len(self.queue)} URLs from queue"
                )
            except Exception as e:
                logger.warning(f"[{self.site_name}] Failed to load queue: {e}")
                self.queue = []

        if self.completed_file.exists():
            try:
                with open(self.completed_file, "rb") as f:
                    self.completed = pickle.load(f)
                logger.info(
                    f"[{self.site_name}] Loaded {len(self.completed)} completed URLs"
                )
            except Exception as e:
                logger.warning(f"[{self.site_name}] Failed to load completed: {e}")
                self.completed = set()

    def save_state(self):
        """現在の状態を保存"""
        try:
            with open(self.queue_file, "wb") as f:
                pickle.dump(self.queue, f)

            with open(self.completed_file, "wb") as f:
                pickle.dump(self.completed, f)

            logger.debug(
                f"[{self.site_name}] Saved state: {len(self.queue)} pending, {len(self.completed)} completed"
            )
        except Exception as e:
            logger.error(f"[{self.site_name}] Failed to save state: {e}")

    def add_urls(self, urls: List[str]) -> int:
        """
        URLをキューに追加

        Args:
            urls: 追加するURLのリスト

        Returns:
            int: 実際に追加された新規URL数
        """
        new_urls = []
        for url in urls:
            if url and url not in self.completed and url not in self.queue:
                new_urls.append(url)
                self.queue.append(url)

        if new_urls:
            logger.info(f"[{self.site_name}] Added {len(new_urls)} new URLs to queue")
            self.save_state()

        return len(new_urls)

    def get_next_batch(self, batch_size: int = 10) -> List[str]:
        """
        次のバッチを取得

        Args:
            batch_size: バッチサイズ

        Returns:
            List[str]: 処理対象のURL一覧
        """
        batch = self.queue[:batch_size]
        self.queue = self.queue[batch_size:]
        return batch

    def mark_completed(self, url: str):
        """URLを完了済みとしてマーク"""
        self.completed.add(url)
        if url in self.queue:
            self.queue.remove(url)
        self.save_state()

    def mark_failed(self, url: str, error: str):
        """
        URLを失敗としてマーク（ログ記録後、完了済みとして扱う）

        Args:
            url: 失敗したURL
            error: エラー内容
        """
        logger.warning(f"[{self.site_name}] Failed URL: {url} - {error}")
        self.mark_completed(url)  # 無限ループ防止のため完了済みとする

    def get_stats(self) -> Dict[str, int]:
        """統計情報を取得"""
        return {
            "pending": len(self.queue),
            "completed": len(self.completed),
            "total": len(self.queue) + len(self.completed),
        }

    def reset(self):
        """キューをリセット（テスト用）"""
        self.queue = []
        self.completed = set()
        self.save_state()
        logger.info(f"[{self.site_name}] Queue reset")


class RateLimiter:
    """
    レート制限管理クラス
    サイトごとの適切な待機時間を管理
    """

    def __init__(self, min_delay: float = 3.0, max_delay: float = 8.0):
        """
        Args:
            min_delay: 最小待機時間（秒）
            max_delay: 最大待機時間（秒）
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0

    def wait(self):
        """適切な待機時間を取る"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        delay = random.uniform(self.min_delay, self.max_delay)

        if elapsed < delay:
            sleep_time = delay - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_request_time = time.time()


def extract_contractor_info(
    soup: BeautifulSoup, selectors: Dict[str, str]
) -> Dict[str, Any]:
    """
    元請会社情報を汎用的に抽出

    Args:
        soup: BeautifulSoupオブジェクト
        selectors: セレクタ辞書

    Returns:
        Dict[str, Any]: 抽出された会社情報
    """
    from shared.formatters import (
        clean_phone_number,
        normalize_address,
        normalize_company_name,
    )

    contractor_info = {}

    # 会社情報セクションを探す
    company_section = None
    for selector in selectors.get("company_section", "").split(", "):
        if selector:
            company_section = soup.select_one(selector)
            if company_section:
                break

    if company_section:
        # 会社名
        for selector in selectors.get("company_name", "").split(", "):
            if selector:
                name_elem = company_section.select_one(selector)
                if name_elem:
                    raw_name = name_elem.get_text(strip=True)
                    contractor_info["contractor_company_name"] = normalize_company_name(
                        raw_name
                    )
                    break

        # 電話番号
        for selector in selectors.get("company_phone", "").split(", "):
            if selector:
                phone_elem = company_section.select_one(selector)
                if phone_elem:
                    phone_text = phone_elem.get_text(strip=True)
                    cleaned_phone = clean_phone_number(phone_text)
                    if cleaned_phone:
                        contractor_info["contractor_phone"] = cleaned_phone
                        break

        # 免許番号
        license_selector = selectors.get("company_license")
        if license_selector:
            license_elem = company_section.select_one(license_selector)
            if license_elem:
                contractor_info["contractor_license_number"] = license_elem.get_text(
                    strip=True
                )

        # 会社住所
        address_selector = selectors.get("company_address")
        if address_selector:
            address_elem = company_section.select_one(address_selector)
            if address_elem:
                raw_address = address_elem.get_text(strip=True)
                contractor_info["contractor_address"] = normalize_address(raw_address)

        # 担当者名
        contact_selector = selectors.get("contact_person")
        if contact_selector:
            contact_elem = company_section.select_one(contact_selector)
            if contact_elem:
                contractor_info["contractor_contact_person"] = contact_elem.get_text(
                    strip=True
                )

    # 会社情報が見つからない場合は、ページ全体から会社名を探す
    if not contractor_info.get("contractor_company_name"):
        # 会社名パターンで検索
        company_pattern = re.compile(r"((?:株式会社|有限会社|合同会社)[^。、\s]{2,20})")
        company_text = soup.get_text()
        matches = company_pattern.findall(company_text)
        if matches:
            # 最初に見つかった会社名を使用
            contractor_info["contractor_company_name"] = normalize_company_name(
                matches[0]
            )

    return contractor_info


def find_next_page_url(
    soup: BeautifulSoup, current_url: str, selectors: List[str]
) -> Optional[str]:
    """
    次ページのURLを汎用的に探す

    Args:
        soup: BeautifulSoupオブジェクト
        current_url: 現在のURL
        selectors: 次ページリンクのセレクタリスト

    Returns:
        Optional[str]: 次ページのURL
    """
    # セレクタベースで検索
    for selector in selectors:
        next_elem = soup.select_one(selector)
        if next_elem and next_elem.get("href"):
            return urljoin(current_url, next_elem["href"])

    # ページ番号ベースで検索
    current_page = 1
    page_match = re.search(r"page[=\/](\d+)", current_url)
    if page_match:
        current_page = int(page_match.group(1))

    # 次のページ番号のリンクを探す
    next_page_selectors = [
        f'a[href*="page={current_page + 1}"]',
        f'a[href*="page/{current_page + 1}"]',
        f'a[data-page="{current_page + 1}"]',
    ]

    for selector in next_page_selectors:
        next_elem = soup.select_one(selector)
        if next_elem and next_elem.get("href"):
            return urljoin(current_url, next_elem["href"])

    return None


def extract_table_data(
    soup: BeautifulSoup, target_headers: Dict[str, str]
) -> Dict[str, Any]:
    """
    テーブルから指定項目のデータを抽出

    Args:
        soup: BeautifulSoupオブジェクト
        target_headers: {'header_text': 'field_name'} の辞書

    Returns:
        Dict[str, Any]: 抽出されたデータ
    """
    from shared.formatters import clean_text_content

    extracted_data = {}

    # dlタグから抽出
    for dl in soup.find_all("dl"):
        dt = dl.find("dt")
        dd = dl.find("dd")
        if dt and dd:
            header_text = dt.get_text(strip=True)
            value_text = clean_text_content(dd.get_text())

            for header_key, field_name in target_headers.items():
                if header_key in header_text:
                    extracted_data[field_name] = value_text
                    break

    # table trタグから抽出
    for tr in soup.find_all("tr"):
        th = tr.find("th")
        td = tr.find("td")
        if th and td:
            header_text = th.get_text(strip=True)
            value_text = clean_text_content(td.get_text())

            for header_key, field_name in target_headers.items():
                if header_key in header_text:
                    extracted_data[field_name] = value_text
                    break

    return extracted_data


def create_property_base_data(url: str, site_name: str) -> Dict[str, Any]:
    """
    物件データの基本構造を作成

    Args:
        url: 物件URL
        site_name: サイト名

    Returns:
        Dict[str, Any]: 基本データ構造
    """
    from shared.formatters import extract_listing_id

    return {
        "source_site": site_name,
        "source_url": url,
        "listing_id": extract_listing_id(url, site_name),
        "transaction_type": "売買",
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def batch_process_urls(
    url_queue: URLQueue,
    process_function,
    batch_size: int = 10,
    rate_limiter: Optional[RateLimiter] = None,
) -> List[Dict[str, Any]]:
    """
    URLをバッチ処理

    Args:
        url_queue: URLキューオブジェクト
        process_function: 処理関数
        batch_size: バッチサイズ
        rate_limiter: レート制限オブジェクト

    Returns:
        List[Dict[str, Any]]: 処理結果のリスト
    """
    if rate_limiter is None:
        rate_limiter = RateLimiter()

    stats = url_queue.get_stats()
    logger.info(
        f"Starting batch process: {batch_size} URLs (Pending: {stats['pending']})"
    )

    # バッチを取得
    urls = url_queue.get_next_batch(batch_size)
    if not urls:
        logger.info("No URLs in queue")
        return []

    results = []

    for i, url in enumerate(urls, 1):
        logger.info(f"Processing {i}/{len(urls)}: {url}")

        try:
            # 処理実行
            result = process_function(url)

            if result:
                results.append(result)
                logger.success(
                    f"✓ Successfully processed: {result.get('title', 'Unknown')}"
                )

            # 完了済みとしてマーク
            url_queue.mark_completed(url)

        except Exception as e:
            logger.error(f"✗ Failed to process {url}: {e}")
            url_queue.mark_failed(url, str(e))

        # レート制限（最後の1件以外）
        if i < len(urls):
            rate_limiter.wait()

    logger.info(f"Batch completed. Processed: {len(results)}/{len(urls)}")
    return results


# ================ 以下を最後に追加 ================


def extract_table_data_with_mapping(
    soup: BeautifulSoup, field_mapping: Dict[str, Any]
) -> Dict[str, Any]:
    """
    テーブルデータを汎用的に抽出

    Args:
        soup: BeautifulSoupオブジェクト
        field_mapping: {ヘッダーパターン: (フィールド名, 処理関数)} の辞書

    Example:
        field_mapping = {
            '所在地': ('address', lambda v: normalize_address(re.sub(r'(地図を見る|無料).*', '', v).strip())),
            '土地面積': ('land_area', parse_area),
            '建物面積': ('building_area', parse_area),
            '築年月': ('construction_year', parse_construction_year),
            '構造': ('structure', lambda v: v),
        }
    """
    result = {}

    for tr in soup.find_all("tr"):
        th = tr.find("th")
        td = tr.find("td")
        if th and td:
            header = th.get_text(strip=True)
            value = td.get_text(strip=True)

            # マッピングに基づいて処理
            for key_pattern, (field_name, processor) in field_mapping.items():
                if key_pattern in header:
                    if callable(processor):
                        result[field_name] = processor(value)
                    else:
                        result[field_name] = value
                    break

    return result


def extract_price_japanese(
    soup: BeautifulSoup, selectors: List[str] = None
) -> Dict[str, Any]:
    """
    日本語の価格表記を汎用的に抽出

    Returns:
        dict: {'price': 価格(数値), 'price_raw': 元の文字列}
    """
    if selectors is None:
        selectors = ["td", "span", "div", "p"]

    for selector in selectors:
        for elem in soup.select(selector):
            text = elem.get_text(strip=True)
            if "万円" in text and text[0].isdigit():
                match = re.search(r"(\d{1,5}(?:,\d{3})*(?:\.\d+)?)\s*万円", text)
                if match:
                    return {
                        "price_raw": match.group(0),
                        "price": parse_sale_price(match.group(0)),
                    }
    return {}
