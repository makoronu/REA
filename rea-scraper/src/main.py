#!/usr/bin/env python3
"""
REA Scraper メインエントリーポイント
"""
import argparse
import sys
from datetime import datetime

from loguru import logger
from src.config.database import db_manager
from src.scrapers.base.universal_scraper import UniversalScraper
from src.scrapers.homes.homes_scraper import HomesPropertyScraper


def parse_arguments():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(description="REA - Real Estate Automation Scraper")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # test-homesサブコマンド
    test_homes_parser = subparsers.add_parser("test-homes", help="Test Homes scraper")
    test_homes_parser.add_argument("--url", help="Specific URL to scrape")
    test_homes_parser.add_argument(
        "--property-type",
        choices=["kodate", "mansion"],
        default="kodate",
        help="Property type to scrape",
    )
    test_homes_parser.add_argument(
        "--show-sample", action="store_true", help="Show sample scraped data"
    )
    test_homes_parser.add_argument(
        "--save", action="store_true", help="Save to database"
    )
    test_homes_parser.add_argument(
        "--detail",
        action="store_true",
        help="Scrape detail pages (slower but more complete)",
    )
    test_homes_parser.add_argument(
        "--max-properties",
        type=int,
        default=5,
        help="Maximum number of properties to scrape in detail mode",
    )

    # collect-urlsサブコマンド
    collect_parser = subparsers.add_parser(
        "collect-urls", help="Collect property URLs from listing pages"
    )
    collect_parser.add_argument("--url", help="Base URL to start collection")
    collect_parser.add_argument(
        "--property-type",
        choices=["kodate", "mansion", "tochi"],
        default="kodate",
        help="Property type",
    )
    collect_parser.add_argument(
        "--max-pages", type=int, default=10, help="Maximum pages to collect"
    )

    # process-batchサブコマンド
    batch_parser = subparsers.add_parser(
        "process-batch", help="Process a batch of collected URLs"
    )
    batch_parser.add_argument(
        "--batch-size", type=int, default=10, help="Number of properties to process"
    )
    batch_parser.add_argument("--save", action="store_true", help="Save to database")
    batch_parser.add_argument(
        "--show-sample", action="store_true", help="Show sample data"
    )

    # process-allサブコマンド
    all_parser = subparsers.add_parser(
        "process-all", help="Process all remaining URLs with intervals"
    )
    all_parser.add_argument(
        "--batch-size", type=int, default=10, help="Properties per batch"
    )
    all_parser.add_argument(
        "--interval", type=int, default=300, help="Seconds between batches"
    )
    all_parser.add_argument("--save", action="store_true", help="Save to database")

    # queue-statsサブコマンド
    stats_parser = subparsers.add_parser("queue-stats", help="Show queue statistics")
    stats_parser.add_argument("--reset", action="store_true", help="Reset the queue")

    # test-athomeサブコマンド
    test_athome_parser = subparsers.add_parser(
        "test-athome", help="Test AtHome scraper"
    )
    test_athome_parser.add_argument("--url", help="Specific URL to scrape")
    test_athome_parser.add_argument(
        "--show-sample", action="store_true", help="Show sample scraped data"
    )

    # test-suumoサブコマンド
    test_suumo_parser = subparsers.add_parser("test-suumo", help="Test SUUMO scraper")
    test_suumo_parser.add_argument("--url", help="Specific URL to scrape")
    test_suumo_parser.add_argument(
        "--show-sample", action="store_true", help="Show sample scraped data"
    )

    # test-universalサブコマンド
    test_universal_parser = subparsers.add_parser(
        "test-universal", help="Test universal scraper"
    )
    test_universal_parser.add_argument("url", help="URL to scrape")
    test_universal_parser.add_argument(
        "--show-raw", action="store_true", help="Show raw extracted data"
    )

    # runサブコマンド
    run_parser = subparsers.add_parser("run", help="Run scheduled scraping")
    run_parser.add_argument(
        "--sites",
        nargs="+",
        choices=["homes", "athome", "suumo"],
        default=["homes"],
        help="Sites to scrape",
    )
    run_parser.add_argument(
        "--interval", type=int, default=3600, help="Interval between runs (seconds)"
    )

    return parser.parse_args()


def test_homes_scraper(args):
    """ホームズスクレイパーのテスト"""
    logger.info("Starting Homes scraper test...")

    scraper = HomesPropertyScraper()

    # URLの決定
    if args.url:
        test_url = args.url
    else:
        # デフォルトURL（北海道）
        if args.property_type == "mansion":
            test_url = "https://www.homes.co.jp/mansion/hokkaido/list/"
        else:
            test_url = "https://www.homes.co.jp/kodate/hokkaido/list/"

    logger.info(f"Testing with URL: {test_url}")

    # スクレイピング実行（詳細ページ対応）
    if args.detail:
        # 詳細ページクロールモード
        max_properties = args.max_properties or 5
        logger.info(f"Scraping with detail pages (max: {max_properties})")
        properties = scraper.scrape_all_properties(
            test_url, max_properties=max_properties
        )
    else:
        # 一覧ページのみ（従来モード）
        properties = scraper.scrape_listing_page(test_url)

    logger.info(f"Scraped {len(properties)} properties")

    if args.show_sample and properties:
        logger.info("\n=== Sample Property ===")
        sample = properties[0]
        for key, value in sample.items():
            logger.info(f"{key}: {value}")

    if args.save and properties:
        logger.info("Saving to database...")
        for prop in properties:
            db_manager.save_property(prop)
        logger.info(f"Saved {len(properties)} properties")

    scraper.close()


def collect_urls_command(args):
    """URL収集コマンド"""
    logger.info("Starting URL collection...")

    scraper = HomesPropertyScraper()

    # URLの決定
    if args.url:
        base_url = args.url
    else:
        base_url = f"https://www.homes.co.jp/{args.property_type}/hokkaido/list/"

    # URL収集
    collected = scraper.collect_property_urls(base_url, max_pages=args.max_pages)

    # 統計情報表示
    stats = scraper.get_queue_stats()
    logger.info(
        f"""
    URL Collection completed:
    - Collected: {collected} URLs
    - Total in queue: {stats['pending']}
    - Already processed: {stats['completed']}
    """
    )

    scraper.close()


def process_batch_command(args):
    """バッチ処理コマンド"""
    logger.info("Processing batch...")

    scraper = HomesPropertyScraper()

    # データベース保存フラグ
    scraper.save_to_db = args.save

    # バッチ処理
    properties = scraper.process_batch(batch_size=args.batch_size)

    # 結果表示
    logger.info(f"Processed {len(properties)} properties")

    if args.show_sample and properties:
        logger.info("\nSample properties:")
        for i, prop in enumerate(properties[:3], 1):
            logger.info(
                f"""
            Property {i}:
            - Title: {prop.get('title')}
            - Price: {prop.get('price_raw')}
            - Address: {prop.get('address')}
            - Company: {prop.get('contractor_company_name', 'Not found')}
            - Phone: {prop.get('contractor_phone', 'Not found')}
            """
            )

    # 統計情報
    stats = scraper.get_queue_stats()
    logger.info(f"Remaining in queue: {stats['pending']}")

    scraper.close()


def process_all_command(args):
    """全URL処理コマンド"""
    logger.info("Processing all remaining URLs...")

    scraper = HomesPropertyScraper()

    # データベース保存フラグ
    scraper.save_to_db = args.save

    # 全処理
    total = scraper.process_all_remaining(
        batch_size=args.batch_size, batch_interval=args.interval
    )

    logger.info(f"Processing completed. Total processed: {total}")

    scraper.close()


def queue_stats_command(args):
    """キュー統計表示コマンド"""
    scraper = HomesPropertyScraper()

    stats = scraper.get_queue_stats()

    logger.info(
        f"""
    Queue Statistics:
    - Pending: {stats['pending']} URLs
    - Completed: {stats['completed']} URLs
    - Total: {stats['total']} URLs
    """
    )

    if args.reset:
        scraper.reset_queue()
        logger.info("Queue has been reset")

    scraper.close()


def test_athome_scraper(args):
    """AtHomeスクレイパーのテスト"""
    logger.warning("AtHome scraper not implemented yet")
    # TODO: 実装


def test_suumo_scraper(args):
    """SUUMOスクレイパーのテスト"""
    logger.warning("SUUMO scraper not implemented yet")
    # TODO: 実装


def test_universal_scraper(args):
    """汎用スクレイパーのテスト"""
    logger.info(f"Testing universal scraper with: {args.url}")

    scraper = UniversalScraper()
    result = scraper.scrape(args.url)

    if result:
        logger.info(f"Successfully scraped: {result.get('title', 'Unknown')}")
        if args.show_raw:
            import json

            logger.info(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        logger.error("Failed to scrape")

    scraper.close()


def run_scraper(args):
    """定期実行"""
    logger.info(f"Starting scheduled scraping for sites: {args.sites}")
    logger.info(f"Interval: {args.interval} seconds")

    # TODO: スケジューラー実装
    logger.warning("Scheduler not implemented yet")


def main():
    """メインエントリーポイント"""
    args = parse_arguments()

    logger.info("REA Scraper starting...")
    logger.info(f"Command: {args.command}")

    # コマンドに応じて処理を分岐
    if args.command == "test-homes":
        test_homes_scraper(args)
    elif args.command == "collect-urls":
        collect_urls_command(args)
    elif args.command == "process-batch":
        process_batch_command(args)
    elif args.command == "process-all":
        process_all_command(args)
    elif args.command == "queue-stats":
        queue_stats_command(args)
    elif args.command == "test-athome":
        test_athome_scraper(args)
    elif args.command == "test-suumo":
        test_suumo_scraper(args)
    elif args.command == "test-universal":
        test_universal_scraper(args)
    elif args.command == "run":
        run_scraper(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
