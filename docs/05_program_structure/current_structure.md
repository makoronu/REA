# 🏗️ REAプログラム構造仕様

## 📋 生成情報
- **生成日時**: 2025-09-11 20:01:56
- **プロジェクトパス**: /Users/yaguchimakoto/my_programing/REA
- **総ファイル数**: 213
- **総関数数**: 387
- **総クラス数**: 60
- **総行数**: 13,071

## 📈 モジュール別構造

| No | ファイル | 行数 | 関数数 | クラス数 | 用途 |
|----|----------|------|--------|----------|------|
| 1 | `rea-admin/node_modules/flatted/python/flatted.py` | 149 | 15 | 2 | ユーティリティモジュール |
| 2 | `rea-scraper/src/scraper_manager.py` | 1 | 0 | 0 | スクレイピング機能 |
| 3 | `rea-scraper/src/__init__.py` | 1 | 0 | 0 | スクレイピング機能 |
| 4 | `rea-scraper/src/scheduler.py` | 1 | 0 | 0 | スクレイピング機能 |
| 5 | `rea-scraper/src/main.py` | 357 | 11 | 0 | メインエントリーポイント |
| 6 | `rea-scraper/src/core/image_downloader.py` | 1 | 0 | 0 | スクレイピング機能 |
| 7 | `rea-scraper/src/core/base_coordinator.py` | 0 | 0 | 0 | スクレイピング機能 |
| 8 | `rea-scraper/src/core/data_processor.py` | 1 | 0 | 0 | スクレイピング機能 |
| 9 | `rea-scraper/src/core/__init__.py` | 1 | 0 | 0 | スクレイピング機能 |
| 10 | `rea-scraper/src/core/base_scraper.py` | 1 | 0 | 0 | スクレイピング機能 |
| 11 | `rea-scraper/src/core/base_collector.py` | 0 | 0 | 0 | スクレイピング機能 |
| 12 | `rea-scraper/src/core/error_handler.py` | 1 | 0 | 0 | スクレイピング機能 |
| 13 | `rea-scraper/src/core/scheduler.py` | 1 | 0 | 0 | スクレイピング機能 |
| 14 | `rea-scraper/src/core/browser_manager.py` | 1 | 0 | 0 | スクレイピング機能 |
| 15 | `rea-scraper/src/config/portal_list.py` | 1 | 0 | 0 | 設定ファイル |
| 16 | `rea-scraper/src/config/scraper_config.py` | 1 | 0 | 0 | 設定ファイル |
| 17 | `rea-scraper/src/config/proxy_config.py` | 1 | 0 | 0 | 設定ファイル |
| 18 | `rea-scraper/src/config/__init__.py` | 1 | 0 | 0 | 設定ファイル |
| 19 | `rea-scraper/src/config/schedule_config.py` | 1 | 0 | 0 | 設定ファイル |
| 20 | `rea-scraper/src/config/settings.py` | 199 | 2 | 1 | 設定ファイル |
| 21 | `rea-scraper/src/learning/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 22 | `rea-scraper/src/utils/validator.py` | 1 | 0 | 0 | スクレイピング機能 |
| 23 | `rea-scraper/src/utils/selenium_manager.py` | 310 | 12 | 1 | スクレイピング機能 |
| 24 | `rea-scraper/src/utils/__init__.py` | 1 | 0 | 0 | スクレイピング機能 |
| 25 | `rea-scraper/src/utils/logger.py` | 250 | 15 | 1 | スクレイピング機能 |
| 26 | `rea-scraper/src/utils/diff_checker.py` | 1 | 0 | 0 | スクレイピング機能 |
| 27 | `rea-scraper/src/utils/process_manager.py` | 352 | 13 | 2 | スクレイピング機能 |
| 28 | `rea-scraper/src/utils/normalizer.py` | 1 | 0 | 0 | スクレイピング機能 |
| 29 | `rea-scraper/src/utils/decorators.py` | 449 | 30 | 0 | スクレイピング機能 |
| 30 | `rea-scraper/src/storage/url_storage.py` | 0 | 0 | 0 | スクレイピング機能 |
| 31 | `rea-scraper/src/storage/progress_tracker.py` | 0 | 0 | 0 | スクレイピング機能 |
| 32 | `rea-scraper/src/storage/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 33 | `rea-scraper/src/sites/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 34 | `rea-scraper/src/sites/homes/scraper.py` | 0 | 0 | 0 | スクレイピング機能 |
| 35 | `rea-scraper/src/sites/homes/config.py` | 0 | 0 | 0 | 設定ファイル |
| 36 | `rea-scraper/src/sites/homes/collector.py` | 0 | 0 | 0 | スクレイピング機能 |
| 37 | `rea-scraper/src/sites/homes/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 38 | `rea-scraper/src/sites/homes/selectors.py` | 0 | 0 | 0 | スクレイピング機能 |
| 39 | `rea-scraper/src/sites/athome/scraper.py` | 0 | 0 | 0 | スクレイピング機能 |
| 40 | `rea-scraper/src/sites/athome/config.py` | 0 | 0 | 0 | 設定ファイル |
| 41 | `rea-scraper/src/sites/athome/collector.py` | 0 | 0 | 0 | スクレイピング機能 |
| 42 | `rea-scraper/src/sites/athome/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 43 | `rea-scraper/src/sites/athome/selectors.py` | 0 | 0 | 0 | スクレイピング機能 |
| 44 | `rea-scraper/src/sites/suumo/scraper.py` | 0 | 0 | 0 | スクレイピング機能 |
| 45 | `rea-scraper/src/sites/suumo/config.py` | 0 | 0 | 0 | 設定ファイル |
| 46 | `rea-scraper/src/sites/suumo/collector.py` | 0 | 0 | 0 | スクレイピング機能 |
| 47 | `rea-scraper/src/sites/suumo/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 48 | `rea-scraper/src/sites/suumo/selectors.py` | 0 | 0 | 0 | スクレイピング機能 |
| 49 | `rea-scraper/src/data_processor/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 50 | `rea-scraper/src/ai/universal_extractor.py` | 0 | 0 | 0 | スクレイピング機能 |
| 51 | `rea-scraper/src/ai/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 52 | `rea-scraper/src/ai/pattern_learner.py` | 0 | 0 | 0 | スクレイピング機能 |
| 53 | `rea-scraper/src/ai/quality_evaluator.py` | 0 | 0 | 0 | スクレイピング機能 |
| 54 | `rea-scraper/src/commands/batch_process.py` | 0 | 0 | 0 | スクレイピング機能 |
| 55 | `rea-scraper/src/commands/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 56 | `rea-scraper/src/commands/scrape_detail.py` | 0 | 0 | 0 | スクレイピング機能 |
| 57 | `rea-scraper/src/commands/collect_urls.py` | 0 | 0 | 0 | スクレイピング機能 |
| 58 | `rea-scraper/src/scrapers/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 59 | `rea-scraper/src/scrapers/reins/reins_config.py` | 1 | 0 | 0 | 設定ファイル |
| 60 | `rea-scraper/src/scrapers/reins/reins_login.py` | 1 | 0 | 0 | スクレイピング機能 |
| 61 | `rea-scraper/src/scrapers/reins/reins_scraper.py` | 1 | 0 | 0 | スクレイピング機能 |
| 62 | `rea-scraper/src/scrapers/reins/__init__.py` | 1 | 0 | 0 | スクレイピング機能 |
| 63 | `rea-scraper/src/scrapers/reins/reins_parser.py` | 1 | 0 | 0 | スクレイピング機能 |
| 64 | `rea-scraper/src/scrapers/reins/reins_selectors.py` | 1 | 0 | 0 | スクレイピング機能 |
| 65 | `rea-scraper/src/scrapers/jimoty/jimoty_selectors.py` | 1 | 0 | 0 | スクレイピング機能 |
| 66 | `rea-scraper/src/scrapers/jimoty/__init__.py` | 1 | 0 | 0 | スクレイピング機能 |
| 67 | `rea-scraper/src/scrapers/jimoty/jimoty_config.py` | 1 | 0 | 0 | 設定ファイル |
| 68 | `rea-scraper/src/scrapers/jimoty/jimoty_parser.py` | 1 | 0 | 0 | スクレイピング機能 |
| 69 | `rea-scraper/src/scrapers/jimoty/jimoty_login.py` | 1 | 0 | 0 | スクレイピング機能 |
| 70 | `rea-scraper/src/scrapers/jimoty/jimoty_scraper.py` | 1 | 0 | 0 | スクレイピング機能 |
| 71 | `rea-scraper/src/scrapers/universal/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 72 | `rea-scraper/src/scrapers/homes/homes_login.py` | 1 | 0 | 0 | スクレイピング機能 |
| 73 | `rea-scraper/src/scrapers/homes/homes_parser.py` | 1 | 0 | 0 | スクレイピング機能 |
| 74 | `rea-scraper/src/scrapers/homes/__init__.py` | 1 | 0 | 0 | スクレイピング機能 |
| 75 | `rea-scraper/src/scrapers/homes/homes_scraper_v2.py` | 0 | 0 | 0 | スクレイピング機能 |
| 76 | `rea-scraper/src/scrapers/homes/homes_selectors.py` | 1 | 0 | 0 | スクレイピング機能 |
| 77 | `rea-scraper/src/scrapers/homes/homes_scraper_original_backup.py` | 628 | 25 | 2 | スクレイピング機能 |
| 78 | `rea-scraper/src/scrapers/homes/homes_config.py` | 1 | 0 | 0 | 設定ファイル |
| 79 | `rea-scraper/src/scrapers/homes/homes_scraper.py` | 308 | 13 | 1 | スクレイピング機能 |
| 80 | `rea-scraper/src/scrapers/athome/athome_parser.py` | 1 | 0 | 0 | スクレイピング機能 |
| 81 | `rea-scraper/src/scrapers/athome/athome_scraper.py` | 1 | 0 | 0 | スクレイピング機能 |
| 82 | `rea-scraper/src/scrapers/athome/athome_login.py` | 1 | 0 | 0 | スクレイピング機能 |
| 83 | `rea-scraper/src/scrapers/athome/__init__.py` | 1 | 0 | 0 | スクレイピング機能 |
| 84 | `rea-scraper/src/scrapers/athome/athome_config.py` | 1 | 0 | 0 | 設定ファイル |
| 85 | `rea-scraper/src/scrapers/athome/athome_selectors.py` | 1 | 0 | 0 | スクレイピング機能 |
| 86 | `rea-scraper/src/scrapers/suumo/suumo_login.py` | 1 | 0 | 0 | スクレイピング機能 |
| 87 | `rea-scraper/src/scrapers/suumo/suumo_selectors.py` | 1 | 0 | 0 | スクレイピング機能 |
| 88 | `rea-scraper/src/scrapers/suumo/suumo_config.py` | 1 | 0 | 0 | 設定ファイル |
| 89 | `rea-scraper/src/scrapers/suumo/suumo_scraper.py` | 1 | 0 | 0 | スクレイピング機能 |
| 90 | `rea-scraper/src/scrapers/suumo/__init__.py` | 1 | 0 | 0 | スクレイピング機能 |
| 91 | `rea-scraper/src/scrapers/suumo/suumo_parser.py` | 1 | 0 | 0 | スクレイピング機能 |
| 92 | `rea-scraper/src/scrapers/base/__init__.py` | 0 | 0 | 0 | スクレイピング機能 |
| 93 | `rea-scraper/src/scrapers/base/base_scraper.py` | 281 | 13 | 1 | スクレイピング機能 |
| 94 | `rea-scraper/src/scrapers/base/universal_scraper.py` | 620 | 24 | 1 | スクレイピング機能 |
| 95 | `rea-api/app/__init__.py` | 1 | 0 | 0 | API関連 |
| 96 | `rea-api/app/main.py` | 39 | 0 | 0 | メインエントリーポイント |
| 97 | `rea-api/app/core/config.py` | 42 | 0 | 2 | 設定ファイル |
| 98 | `rea-api/app/core/database.py` | 52 | 1 | 0 | API関連 |
| 99 | `rea-api/app/core/security.py` | 1 | 0 | 0 | API関連 |
| 100 | `rea-api/app/core/__init__.py` | 1 | 0 | 0 | API関連 |
| 101 | `rea-api/app/utils/image_processor.py` | 1 | 0 | 0 | API関連 |
| 102 | `rea-api/app/utils/validators.py` | 1 | 0 | 0 | API関連 |
| 103 | `rea-api/app/utils/__init__.py` | 1 | 0 | 0 | API関連 |
| 104 | `rea-api/app/models/equipment.py` | 1 | 0 | 0 | API関連 |
| 105 | `rea-api/app/models/user.py` | 1 | 0 | 0 | API関連 |
| 106 | `rea-api/app/models/property.py` | 65 | 1 | 1 | API関連 |
| 107 | `rea-api/app/models/__init__.py` | 1 | 0 | 0 | API関連 |
| 108 | `rea-api/app/schemas/equipment.py` | 1 | 0 | 0 | API関連 |
| 109 | `rea-api/app/schemas/user.py` | 1 | 0 | 0 | API関連 |
| 110 | `rea-api/app/schemas/property.py` | 76 | 0 | 7 | API関連 |
| 111 | `rea-api/app/schemas/__init__.py` | 1 | 0 | 0 | API関連 |
| 112 | `rea-api/app/crud/equipment.py` | 1 | 0 | 0 | API関連 |
| 113 | `rea-api/app/crud/user.py` | 1 | 0 | 0 | API関連 |
| 114 | `rea-api/app/crud/property.py` | 167 | 9 | 1 | API関連 |
| 115 | `rea-api/app/crud/__init__.py` | 1 | 0 | 0 | API関連 |
| 116 | `rea-api/app/api/__init__.py` | 1 | 0 | 0 | API関連 |
| 117 | `rea-api/app/api/dependencies.py` | 21 | 1 | 0 | API関連 |
| 118 | `rea-api/app/api/api_v1/__init__.py` | 0 | 0 | 0 | API関連 |
| 119 | `rea-api/app/api/api_v1/api.py` | 6 | 0 | 0 | API関連 |
| 120 | `rea-api/app/api/api_v1/endpoints/metadata.py` | 372 | 6 | 0 | API関連 |
| 121 | `rea-api/app/api/api_v1/endpoints/properties.py` | 114 | 8 | 0 | API関連 |
| 122 | `rea-api/app/api/api_v1/endpoints/__init__.py` | 0 | 0 | 0 | API関連 |
| 123 | `rea-api/app/api/endpoints/equipment.py` | 1 | 0 | 0 | API関連 |
| 124 | `rea-api/app/api/endpoints/properties.py` | 1 | 0 | 0 | API関連 |
| 125 | `rea-api/app/api/endpoints/__init__.py` | 1 | 0 | 0 | API関連 |
| 126 | `rea-api/alembic/env.py` | 77 | 2 | 0 | API関連 |
| 127 | `rea-api/alembic/versions/c4e23b46d77e_add_contractor_company_columns.py` | 28 | 2 | 0 | API関連 |
| 128 | `rea-api/alembic/versions/2d259ad1652c_add_contractor_company_columns.py` | 28 | 2 | 0 | API関連 |
| 129 | `rea-publisher/src/__init__.py` | 1 | 0 | 0 | モジュール初期化 |
| 130 | `rea-publisher/src/main.py` | 1 | 0 | 0 | メインエントリーポイント |
| 131 | `rea-publisher/src/publisher_manager.py` | 1 | 0 | 0 | 機能モジュール |
| 132 | `rea-publisher/src/core/publication_manager.py` | 1 | 0 | 0 | 機能モジュール |
| 133 | `rea-publisher/src/core/base_publisher.py` | 1 | 0 | 0 | 機能モジュール |
| 134 | `rea-publisher/src/core/__init__.py` | 1 | 0 | 0 | モジュール初期化 |
| 135 | `rea-publisher/src/utils/result_manager.py` | 1 | 0 | 0 | 機能モジュール |
| 136 | `rea-publisher/src/utils/data_converter.py` | 1 | 0 | 0 | 機能モジュール |
| 137 | `rea-publisher/src/utils/image_uploader.py` | 1 | 0 | 0 | 機能モジュール |
| 138 | `rea-publisher/src/utils/__init__.py` | 1 | 0 | 0 | モジュール初期化 |
| 139 | `rea-publisher/src/publishers/homes_publisher.py` | 1 | 0 | 0 | 機能モジュール |
| 140 | `rea-publisher/src/publishers/reins_publisher.py` | 1 | 0 | 0 | 機能モジュール |
| 141 | `rea-publisher/src/publishers/__init__.py` | 1 | 0 | 0 | モジュール初期化 |
| 142 | `rea-publisher/src/publishers/wordpress_publisher.py` | 1 | 0 | 0 | 機能モジュール |
| 143 | `rea-publisher/src/publishers/suumo_publisher.py` | 1 | 0 | 0 | 機能モジュール |
| 144 | `shared/config.py` | 0 | 0 | 0 | 設定ファイル |
| 145 | `shared/scrapers_common.py` | 477 | 18 | 2 | スクレイピング機能 |
| 146 | `shared/formatters.py` | 315 | 9 | 0 | 共通ライブラリ |
| 147 | `shared/real_estate_utils.py` | 251 | 8 | 0 | 共通ライブラリ |
| 148 | `shared/validators.py` | 0 | 0 | 0 | 共通ライブラリ |
| 149 | `shared/database.py` | 371 | 10 | 1 | データベース操作 |
| 150 | `shared/constants.py` | 0 | 0 | 0 | 共通ライブラリ |
| 151 | `shared/__init__.py` | 0 | 0 | 0 | 共通ライブラリ |
| 152 | `shared/logger.py` | 0 | 0 | 0 | 共通ライブラリ |
| 153 | `shared/system_utils.py` | 0 | 0 | 0 | 共通ライブラリ |
| 154 | `shared/exceptions.py` | 0 | 0 | 0 | 共通ライブラリ |
| 155 | `shared/path_utils.py` | 44 | 2 | 0 | 共通ライブラリ |
| 156 | `shared/config/constants.py` | 1 | 0 | 0 | 設定ファイル |
| 157 | `shared/config/__init__.py` | 1 | 0 | 0 | 設定ファイル |
| 158 | `shared/config/api_endpoints.py` | 1 | 0 | 0 | 設定ファイル |
| 159 | `shared/utils/formatter.py` | 1 | 0 | 0 | 共通ライブラリ |
| 160 | `shared/utils/__init__.py` | 1 | 0 | 0 | 共通ライブラリ |
| 161 | `shared/utils/logger.py` | 1 | 0 | 0 | 共通ライブラリ |
| 162 | `shared/utils/validation.py` | 1 | 0 | 0 | 共通ライブラリ |
| 163 | `shared/schemas/user_schema.py` | 1 | 0 | 0 | 共通ライブラリ |
| 164 | `shared/schemas/__init__.py` | 1 | 0 | 0 | 共通ライブラリ |
| 165 | `shared/schemas/equipment_schema.py` | 1 | 0 | 0 | 共通ライブラリ |
| 166 | `shared/schemas/property_schema.py` | 1 | 0 | 0 | 共通ライブラリ |
| 167 | `scripts/auto_spec_generator/master_generator.py` | 0 | 0 | 0 | 仕様書生成器 |
| 168 | `scripts/auto_spec_generator/table_detail_generator.py` | 0 | 0 | 0 | 仕様書生成器 |
| 169 | `scripts/auto_spec_generator/auto_claude_briefing.py` | 144 | 8 | 1 | 仕様書生成器 |
| 170 | `scripts/auto_spec_generator/main.py` | 163 | 5 | 1 | メインエントリーポイント |
| 171 | `scripts/auto_spec_generator/analyzers/__init__.py` | 0 | 0 | 0 | 仕様書生成器 |
| 172 | `scripts/auto_spec_generator/analyzers/status_tracker.py` | 0 | 0 | 0 | 仕様書生成器 |
| 173 | `scripts/auto_spec_generator/analyzers/code_analyzer.py` | 149 | 8 | 1 | 仕様書生成器 |
| 174 | `scripts/auto_spec_generator/generators.backup/navigation_generator.py` | 138 | 1 | 1 | 仕様書生成器 |
| 175 | `scripts/auto_spec_generator/generators.backup/shared_generator.py` | 128 | 1 | 1 | 仕様書生成器 |
| 176 | `scripts/auto_spec_generator/generators.backup/scraper_generator.py` | 118 | 1 | 1 | 仕様書生成器 |
| 177 | `scripts/auto_spec_generator/generators.backup/database_generator.py` | 368 | 6 | 1 | 仕様書生成器 |
| 178 | `scripts/auto_spec_generator/generators.backup/claude_memory_generator.py` | 421 | 6 | 1 | 仕様書生成器 |
| 179 | `scripts/auto_spec_generator/generators.backup/claude_generator.py` | 147 | 4 | 1 | 仕様書生成器 |
| 180 | `scripts/auto_spec_generator/generators.backup/__init__.py` | 0 | 0 | 0 | 仕様書生成器 |
| 181 | `scripts/auto_spec_generator/generators.backup/shared_library_analyzer.py` | 448 | 8 | 1 | 仕様書生成器 |
| 182 | `scripts/auto_spec_generator/generators.backup/base_generator.py` | 36 | 6 | 1 | 仕様書生成器 |
| 183 | `scripts/auto_spec_generator/generators.backup/program_structure_generator.py` | 214 | 4 | 1 | 仕様書生成器 |
| 184 | `scripts/auto_spec_generator/generators.backup/claude_briefing_generator.py` | 0 | 0 | 0 | 仕様書生成器 |
| 185 | `scripts/auto_spec_generator/generators.backup/api_generator.py` | 95 | 1 | 1 | 仕様書生成器 |
| 186 | `scripts/auto_spec_generator/generators.backup/generators/navigation_generator.py` | 138 | 1 | 1 | 仕様書生成器 |
| 187 | `scripts/auto_spec_generator/generators.backup/generators/shared_generator.py` | 128 | 1 | 1 | 仕様書生成器 |
| 188 | `scripts/auto_spec_generator/generators.backup/generators/scraper_generator.py` | 118 | 1 | 1 | 仕様書生成器 |
| 189 | `scripts/auto_spec_generator/generators.backup/generators/database_generator.py` | 368 | 6 | 1 | 仕様書生成器 |
| 190 | `scripts/auto_spec_generator/generators.backup/generators/claude_memory_generator.py` | 421 | 6 | 1 | 仕様書生成器 |
| 191 | `scripts/auto_spec_generator/generators.backup/generators/claude_generator.py` | 147 | 4 | 1 | 仕様書生成器 |
| 192 | `scripts/auto_spec_generator/generators.backup/generators/__init__.py` | 0 | 0 | 0 | 仕様書生成器 |
| 193 | `scripts/auto_spec_generator/generators.backup/generators/shared_library_analyzer.py` | 448 | 8 | 1 | 仕様書生成器 |
| 194 | `scripts/auto_spec_generator/generators.backup/generators/base_generator.py` | 36 | 6 | 1 | 仕様書生成器 |
| 195 | `scripts/auto_spec_generator/generators.backup/generators/program_structure_generator.py` | 214 | 4 | 1 | 仕様書生成器 |
| 196 | `scripts/auto_spec_generator/generators.backup/generators/claude_briefing_generator.py` | 0 | 0 | 0 | 仕様書生成器 |
| 197 | `scripts/auto_spec_generator/generators.backup/generators/api_generator.py` | 95 | 1 | 1 | 仕様書生成器 |
| 198 | `scripts/auto_spec_generator/config/__init__.py` | 0 | 0 | 0 | 設定ファイル |
| 199 | `scripts/auto_spec_generator/utils/__init__.py` | 0 | 0 | 0 | 仕様書生成器 |
| 200 | `scripts/auto_spec_generator/scripts/auto_spec_generator/analyzers/code_analyzer.py` | 199 | 6 | 1 | 仕様書生成器 |
| 201 | `scripts/auto_spec_generator/scripts/auto_spec_generator/generators/program_structure_generator.py` | 0 | 0 | 0 | 仕様書生成器 |
| 202 | `scripts/auto_spec_generator/generators/navigation_generator.py` | 138 | 1 | 1 | 仕様書生成器 |
| 203 | `scripts/auto_spec_generator/generators/shared_generator.py` | 128 | 1 | 1 | 仕様書生成器 |
| 204 | `scripts/auto_spec_generator/generators/scraper_generator.py` | 118 | 1 | 1 | 仕様書生成器 |
| 205 | `scripts/auto_spec_generator/generators/database_generator.py` | 163 | 3 | 1 | 仕様書生成器 |
| 206 | `scripts/auto_spec_generator/generators/claude_memory_generator.py` | 162 | 3 | 1 | 仕様書生成器 |
| 207 | `scripts/auto_spec_generator/generators/claude_generator.py` | 147 | 4 | 1 | 仕様書生成器 |
| 208 | `scripts/auto_spec_generator/generators/__init__.py` | 0 | 0 | 0 | 仕様書生成器 |
| 209 | `scripts/auto_spec_generator/generators/shared_library_analyzer.py` | 448 | 8 | 1 | 仕様書生成器 |
| 210 | `scripts/auto_spec_generator/generators/base_generator.py` | 36 | 6 | 1 | 仕様書生成器 |
| 211 | `scripts/auto_spec_generator/generators/program_structure_generator.py` | 214 | 4 | 1 | 仕様書生成器 |
| 212 | `scripts/auto_spec_generator/generators/claude_briefing_generator.py` | 0 | 0 | 0 | 仕様書生成器 |
| 213 | `scripts/auto_spec_generator/generators/api_generator.py` | 95 | 1 | 1 | 仕様書生成器 |

## 📊 統計サマリー
- **平均ファイルサイズ**: 61行
- **関数密度**: 1.8関数/ファイル
- **クラス密度**: 0.3クラス/ファイル

## 🎯 主要モジュール詳細


### rea-admin/node_modules/flatted/python/flatted.py
**行数**: 149  
**複雑度**: 28  
**クラス**: _Known, _String  
**関数**: _array_keys, _object_keys, _is_array, _is_object, _is_string ...他10関数  

### rea-scraper/src/main.py
**行数**: 357  
**複雑度**: 28  
**説明**: REA Scraper メインエントリーポイント...  
**関数**: parse_arguments, test_homes_scraper, collect_urls_command, process_batch_command, process_all_command ...他6関数  

### rea-scraper/src/config/settings.py
**行数**: 199  
**複雑度**: 8  
**説明**: REA Scraper 設定管理
汎用学習スクレイピングシステムの設定を一元管理...  
**クラス**: Settings  
**関数**: get_site_config, validate  

### rea-scraper/src/utils/selenium_manager.py
**行数**: 310  
**複雑度**: 29  
**説明**: Selenium WebDriver管理モジュール
耐障害性・回避策強化版...  
**クラス**: SeleniumManager  
**関数**: __init__, _load_proxies, _get_chrome_options, create_driver, wait_for_element ...他7関数  

### rea-scraper/src/utils/logger.py
**行数**: 250  
**複雑度**: 6  
**説明**: REA Scraper ログ管理
ログの設定、カスタムハンドラー、ログユーティリティ...  
**クラス**: ScrapingLogger  
**関数**: setup_logger, log_property_saved, log_scraping_stats, log_error_with_context, log_learning_progress ...他10関数  

### rea-scraper/src/utils/process_manager.py
**行数**: 352  
**複雑度**: 34  
**説明**: プロセス管理・監視機能
長時間実行のための安全対策...  
**クラス**: ProcessManager, ScraperMonitor  
**関数**: create_systemd_service, create_launchd_plist, __init__, start, is_running ...他8関数  

### rea-scraper/src/utils/decorators.py
**行数**: 449  
**複雑度**: 35  
**説明**: 便利なデコレータ集
リトライ、キャッシュ、エラーハンドリング、パフォーマンス測定など...  
**関数**: retry, measure_time, cache, handle_errors, rate_limit ...他25関数  

### rea-scraper/src/scrapers/homes/homes_scraper_original_backup.py
**行数**: 628  
**複雑度**: 85  
**説明**: ホームズ不動産売買物件スクレイパー
段階的処理・レート制限対応版...  
**クラス**: URLQueue, HomesPropertyScraper  
**関数**: __init__, _load_state, save_state, add_urls, get_next_batch ...他20関数  

### rea-scraper/src/scrapers/homes/homes_scraper.py
**行数**: 308  
**複雑度**: 34  
**説明**: ホームズ不動産売買物件スクレイパー
共通ライブラリ最大活用版...  
**クラス**: HomesPropertyScraper  
**関数**: __init__, collect_property_urls, process_batch, scrape_property_detail, _extract_price ...他8関数  

### rea-scraper/src/scrapers/base/base_scraper.py
**行数**: 281  
**複雑度**: 34  
**説明**: 基底スクレイパークラス
全スクレイパーの共通機能を提供...  
**クラス**: BaseScraper  
**関数**: parse_japanese_number, normalize_address, __init__, get_driver, get_page_source ...他8関数  

### rea-scraper/src/scrapers/base/universal_scraper.py
**行数**: 620  
**複雑度**: 80  
**説明**: 汎用スクレイパー - 未知の不動産サイトでも自動的に物件情報を抽出
完全に構造を知らない状態から学習・抽出する...  
**クラス**: UniversalScraper  
**関数**: __init__, analyze_page_structure, _find_repeated_elements, _have_similar_structure, _get_element_structure ...他19関数  

### rea-api/app/core/config.py
**行数**: 42  
**複雑度**: 1  
**クラス**: Settings, Config  

### rea-api/app/core/database.py
**行数**: 52  
**複雑度**: 3  
**説明**: REA API データベース接続
shared/database.pyを使用して統一管理...  
**関数**: get_db  

### rea-api/app/models/property.py
**行数**: 65  
**複雑度**: 1  
**クラス**: Property  
**関数**: __repr__  

### rea-api/app/schemas/property.py
**行数**: 76  
**複雑度**: 1  
**クラス**: PropertyBase, PropertyCreate, PropertyUpdate, PropertyInDBBase, Property, PropertySearchParams, Config  

### rea-api/app/crud/property.py
**行数**: 167  
**複雑度**: 18  
**クラス**: PropertyCRUD  
**関数**: get_properties, get_property, get_property_by_homes_id, create_property, update_property ...他4関数  

### rea-api/app/api/api_v1/endpoints/metadata.py
**行数**: 372  
**複雑度**: 14  
**説明**: データベースメタデータAPI
テーブル構造、カラム情報、ラベル情報を提供...  
**関数**: get_all_tables, get_table_details, get_table_columns_with_labels, get_enum_values, get_validation_rules ...他1関数  

### rea-api/app/api/api_v1/endpoints/properties.py
**行数**: 114  
**複雑度**: 7  
**関数**: read_properties, read_property, create_property, update_property, delete_property ...他3関数  

### rea-api/alembic/env.py
**行数**: 77  
**複雑度**: 6  
**関数**: run_migrations_offline, run_migrations_online  

### shared/scrapers_common.py
**行数**: 477  
**複雑度**: 71  
**説明**: REAスクレイピング共通処理
URL管理、データ抽出、エラーハンドリング等の共通機能...  
**クラス**: URLQueue, RateLimiter  
**関数**: extract_contractor_info, find_next_page_url, extract_table_data, create_property_base_data, batch_process_urls ...他13関数  

### shared/formatters.py
**行数**: 315  
**複雑度**: 23  
**説明**: REAフォーマット処理統一システム
住所、電話番号、日付等の統一フォーマット処理...  
**関数**: normalize_address, clean_phone_number, extract_listing_id, format_date_japanese, format_area_display ...他4関数  

### shared/real_estate_utils.py
**行数**: 251  
**複雑度**: 26  
**説明**: REA不動産業務専用ユーティリティ
価格計算、利回り計算、築年数計算等の不動産特化機能...  
**関数**: parse_sale_price, parse_area, parse_construction_year, determine_property_type, calculate_property_age ...他3関数  

### shared/database.py
**行数**: 371  
**複雑度**: 11  
**説明**: REA シンプルデータベース接続

【重要】DB接続設定について
========================
このファイルは必ずプロジェクトルートの.envファイルから設定を読み込みます。
.e...  
**クラス**: READatabase  
**関数**: quick_test, get_tables, _load_env, get_connection, test_connection ...他5関数  

### scripts/auto_spec_generator/auto_claude_briefing.py
**行数**: 144  
**複雑度**: 8  
**クラス**: AutoClaudeBriefing  
**関数**: main, __init__, run_full_automation, _update_memory_system, _verify_memory_files ...他3関数  

### scripts/auto_spec_generator/main.py
**行数**: 163  
**複雑度**: 14  
**クラス**: REASpecGeneratorController  
**関数**: __init__, generate_all, _print_summary, display_file_content, display_summary_content  

### scripts/auto_spec_generator/analyzers/code_analyzer.py
**行数**: 149  
**複雑度**: 27  
**クラス**: CodeAnalyzer  
**関数**: __init__, analyze_python_file, _extract_functions, _extract_classes, _extract_imports ...他3関数  

### scripts/auto_spec_generator/generators.backup/navigation_generator.py
**行数**: 138  
**複雑度**: 1  
**クラス**: NavigationGenerator  
**関数**: generate  

### scripts/auto_spec_generator/generators.backup/shared_generator.py
**行数**: 128  
**複雑度**: 2  
**クラス**: SharedGenerator  
**関数**: generate  

### scripts/auto_spec_generator/generators.backup/scraper_generator.py
**行数**: 118  
**複雑度**: 3  
**クラス**: ScraperGenerator  
**関数**: generate  

### scripts/auto_spec_generator/generators.backup/database_generator.py
**行数**: 368  
**複雑度**: 40  
**クラス**: DatabaseGenerator  
**関数**: generate, _generate_fallback_spec, _get_table_purpose_auto, _smart_guess_table_purpose, _pattern_match_purpose ...他1関数  

### scripts/auto_spec_generator/generators.backup/claude_memory_generator.py
**行数**: 421  
**複雑度**: 22  
**クラス**: ClaudeMemoryGenerator  
**関数**: generate, _get_current_project_status, _count_program_files, _get_recent_achievements, _generate_memory_content ...他1関数  

### scripts/auto_spec_generator/generators.backup/claude_generator.py
**行数**: 147  
**複雑度**: 1  
**クラス**: ClaudeGenerator  
**関数**: generate, _generate_database_chunk, _generate_api_chunk, _generate_shared_chunk  

### scripts/auto_spec_generator/generators.backup/shared_library_analyzer.py
**行数**: 448  
**複雑度**: 74  
**クラス**: SharedLibraryAnalyzer  
**関数**: __init__, generate, _analyze_python_file, _extract_file_docstring, _extract_classes_detailed ...他3関数  

### scripts/auto_spec_generator/generators.backup/base_generator.py
**行数**: 36  
**複雑度**: 2  
**クラス**: BaseGenerator  
**関数**: __init__, generate, get_output_dir, save_content, get_timestamp ...他1関数  

### scripts/auto_spec_generator/generators.backup/program_structure_generator.py
**行数**: 214  
**複雑度**: 33  
**クラス**: ProgramStructureGenerator  
**関数**: generate, _classify_file_purpose, _generate_file_detail, _generate_dependency_analysis  

### scripts/auto_spec_generator/generators.backup/api_generator.py
**行数**: 95  
**複雑度**: 4  
**クラス**: APIGenerator  
**関数**: generate  

### scripts/auto_spec_generator/generators.backup/generators/navigation_generator.py
**行数**: 138  
**複雑度**: 1  
**クラス**: NavigationGenerator  
**関数**: generate  

### scripts/auto_spec_generator/generators.backup/generators/shared_generator.py
**行数**: 128  
**複雑度**: 2  
**クラス**: SharedGenerator  
**関数**: generate  

### scripts/auto_spec_generator/generators.backup/generators/scraper_generator.py
**行数**: 118  
**複雑度**: 3  
**クラス**: ScraperGenerator  
**関数**: generate  

### scripts/auto_spec_generator/generators.backup/generators/database_generator.py
**行数**: 368  
**複雑度**: 40  
**クラス**: DatabaseGenerator  
**関数**: generate, _generate_fallback_spec, _get_table_purpose_auto, _smart_guess_table_purpose, _pattern_match_purpose ...他1関数  

### scripts/auto_spec_generator/generators.backup/generators/claude_memory_generator.py
**行数**: 421  
**複雑度**: 22  
**クラス**: ClaudeMemoryGenerator  
**関数**: generate, _get_current_project_status, _count_program_files, _get_recent_achievements, _generate_memory_content ...他1関数  

### scripts/auto_spec_generator/generators.backup/generators/claude_generator.py
**行数**: 147  
**複雑度**: 1  
**クラス**: ClaudeGenerator  
**関数**: generate, _generate_database_chunk, _generate_api_chunk, _generate_shared_chunk  

### scripts/auto_spec_generator/generators.backup/generators/shared_library_analyzer.py
**行数**: 448  
**複雑度**: 74  
**クラス**: SharedLibraryAnalyzer  
**関数**: __init__, generate, _analyze_python_file, _extract_file_docstring, _extract_classes_detailed ...他3関数  

### scripts/auto_spec_generator/generators.backup/generators/base_generator.py
**行数**: 36  
**複雑度**: 2  
**クラス**: BaseGenerator  
**関数**: __init__, generate, get_output_dir, save_content, get_timestamp ...他1関数  

### scripts/auto_spec_generator/generators.backup/generators/program_structure_generator.py
**行数**: 214  
**複雑度**: 33  
**クラス**: ProgramStructureGenerator  
**関数**: generate, _classify_file_purpose, _generate_file_detail, _generate_dependency_analysis  

### scripts/auto_spec_generator/generators.backup/generators/api_generator.py
**行数**: 95  
**複雑度**: 4  
**クラス**: APIGenerator  
**関数**: generate  

### scripts/auto_spec_generator/scripts/auto_spec_generator/analyzers/code_analyzer.py
**行数**: 199  
**複雑度**: 38  
**クラス**: CodeAnalyzer  
**関数**: __init__, get_project_summary, _collect_python_files, _analyze_file, _get_decorator_name ...他1関数  

### scripts/auto_spec_generator/generators/navigation_generator.py
**行数**: 138  
**複雑度**: 1  
**クラス**: NavigationGenerator  
**関数**: generate  

### scripts/auto_spec_generator/generators/shared_generator.py
**行数**: 128  
**複雑度**: 2  
**クラス**: SharedGenerator  
**関数**: generate  

### scripts/auto_spec_generator/generators/scraper_generator.py
**行数**: 118  
**複雑度**: 3  
**クラス**: ScraperGenerator  
**関数**: generate  

### scripts/auto_spec_generator/generators/database_generator.py
**行数**: 163  
**複雑度**: 16  
**クラス**: DatabaseGenerator  
**関数**: generate, _generate_fallback_spec, _get_table_purpose  

### scripts/auto_spec_generator/generators/claude_memory_generator.py
**行数**: 162  
**複雑度**: 14  
**クラス**: ClaudeMemoryGenerator  
**関数**: generate, _get_current_status, _generate_context  

### scripts/auto_spec_generator/generators/claude_generator.py
**行数**: 147  
**複雑度**: 1  
**クラス**: ClaudeGenerator  
**関数**: generate, _generate_database_chunk, _generate_api_chunk, _generate_shared_chunk  

### scripts/auto_spec_generator/generators/shared_library_analyzer.py
**行数**: 448  
**複雑度**: 74  
**クラス**: SharedLibraryAnalyzer  
**関数**: __init__, generate, _analyze_python_file, _extract_file_docstring, _extract_classes_detailed ...他3関数  

### scripts/auto_spec_generator/generators/base_generator.py
**行数**: 36  
**複雑度**: 2  
**クラス**: BaseGenerator  
**関数**: __init__, generate, get_output_dir, save_content, get_timestamp ...他1関数  

### scripts/auto_spec_generator/generators/program_structure_generator.py
**行数**: 214  
**複雑度**: 33  
**クラス**: ProgramStructureGenerator  
**関数**: generate, _classify_file_purpose, _generate_file_detail, _generate_dependency_analysis  

### scripts/auto_spec_generator/generators/api_generator.py
**行数**: 95  
**複雑度**: 4  
**クラス**: APIGenerator  
**関数**: generate  

## 🔗 依存関係分析

### 外部ライブラリ使用状況
- **typing**: 138回使用  
- **pathlib**: 46回使用  
- **sqlalchemy**: 29回使用  
- **base_generator**: 24回使用  
- **datetime**: 22回使用  
- **src**: 21回使用  
- **selenium**: 20回使用  
- **sys**: 16回使用  
- **app**: 14回使用  
- **os**: 13回使用  

### 内部モジュール依存
- **shared.database**: 12回参照  
- **shared.formatters**: 8回参照  
- **shared.scrapers_common**: 4回参照  
- **shared.real_estate_utils**: 4回参照  
- **analyzers.code_analyzer**: 3回参照  
- **generators.database_generator**: 1回参照  
- **generators.api_generator**: 1回参照  
- **generators.scraper_generator**: 1回参照  
- **generators.shared_generator**: 1回参照  
- **generators.shared_library_analyzer**: 1回参照  
