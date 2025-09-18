# 🔬 shared/ ライブラリ完全リファレンス（全関数検出版）

**生成日時**: 自動生成
**分析ファイル数**: 11

## 📋 ファイル一覧

| No | ファイル名 | サイズ | クラス数 | 全関数数 | 行数 | 説明 |
|----|------------|--------|----------|----------|------|------|
| 1 | logger.py | 0KB | 0 | 0 | 1 | - |
| 2 | validators.py | 0KB | 0 | 0 | 1 | - |
| 3 | formatters.py | 7KB | 0 | 9 | 321 | REAフォーマット処理統一システム |
| 4 | path_utils.py | 1KB | 0 | 2 | 47 | REAプロジェクトパス自動設定ユーティリティ |
| 5 | constants.py | 0KB | 0 | 0 | 1 | - |
| 6 | real_estate_utils.py | 6KB | 0 | 7 | 257 | REA不動産業務専用ユーティリティ |
| 7 | exceptions.py | 0KB | 0 | 0 | 1 | - |
| 8 | config.py | 0KB | 0 | 0 | 1 | - |
| 9 | scrapers_common.py | 15KB | 2 | 23 | 513 | REAスクレイピング共通処理 |
| 10 | database.py | 12KB | 1 | 18 | 378 | REA シンプルデータベース接続 |
| 11 | system_utils.py | 0KB | 0 | 0 | 1 | - |

## 📁 logger.py

- **サイズ**: 0KB
- **行数**: 1行
- **総関数数**: 0個

---

## 📁 validators.py

- **サイズ**: 0KB
- **行数**: 1行
- **総関数数**: 0個

---

## 📁 formatters.py

### 📝 ファイル説明
```
REAフォーマット処理統一システム
住所、電話番号、日付等の統一フォーマット処理
```

- **サイズ**: 7KB
- **行数**: 321行
- **総関数数**: 9個

### 📦 インポート詳細

- `import re`
- `from typing import Optional`

### ⚙️ モジュールレベル関数

#### `normalize_address(address: str) -> str`

**説明**:
```
住所を正規化  Args: address: 住所文字列
```

#### `clean_phone_number(phone_text: str) -> Optional[str]`

**説明**:
```
電話番号をクリーニング  Args: phone_text: 電話番号文字列
```

#### `extract_listing_id(url: str, prefix: str = "homes") -> Optional[str]`

**説明**:
```
URLから物件ID抽出  Args: url: 物件URL
```

#### `format_date_japanese(date_str: str) -> str`

**説明**:
```
日付を日本語形式にフォーマット  Args: date_str: 日付文字列
```

#### `format_area_display(area: Optional[float], unit: str = "㎡") -> str`

**説明**:
```
面積を表示用にフォーマット  Args: area: 面積
```

#### `clean_text_content(text: str) -> str`

**説明**:
```
テキストコンテンツをクリーニング  Args: text: クリーニング対象のテキスト
```

#### `normalize_company_name(company_name: str) -> str`

**説明**:
```
会社名を正規化  Args: company_name: 会社名
```

#### `extract_numeric_value(text: str) -> Optional[float]`

**説明**:
```
テキストから数値を抽出  Args: text: テキスト
```

#### `format_floor_plan(floor_plan: str) -> str`

**説明**:
```
間取りを正規化  Args: floor_plan: 間取り文字列
```

---

## 📁 path_utils.py

### 📝 ファイル説明
```
REAプロジェクトパス自動設定ユーティリティ
```

- **サイズ**: 1KB
- **行数**: 47行
- **総関数数**: 2個

### 📦 インポート詳細

- `import sys`
- `from pathlib import Path`
- `from typing import Tuple`

### ⚙️ モジュールレベル関数

#### `setup_project_paths() -> Tuple[Path, Path]`

**説明**:
```
プロジェクトパスを自動設定  Returns: tuple: (project_root, rea_scraper_root)
```

#### `print_path_debug() `

**説明**:
```
パス設定のデバッグ情報を表示
```

---

## 📁 constants.py

- **サイズ**: 0KB
- **行数**: 1行
- **総関数数**: 0個

---

## 📁 real_estate_utils.py

### 📝 ファイル説明
```
REA不動産業務専用ユーティリティ
価格計算、利回り計算、築年数計算等の不動産特化機能
```

- **サイズ**: 6KB
- **行数**: 257行
- **総関数数**: 7個

### 📦 インポート詳細

- `import re`
- `from datetime import datetime`
- `from typing import Optional`

### ⚙️ モジュールレベル関数

#### `parse_sale_price(price_text: str) -> Optional[float]`

**説明**:
```
売買価格をパース  Args: price_text: 価格文字列（例: "1200万円", "1億2000万円"）
```

#### `parse_area(area_text: str) -> Optional[float]`

**説明**:
```
面積をパース  Args: area_text: 面積文字列（例: "50.5㎡", "100平米"）
```

#### `parse_construction_year(text: str) -> Optional[int]`

**説明**:
```
築年月から年を抽出  Args: text: 築年月文字列（例: "令和3年", "2021年", "平成30年"）
```

#### `determine_property_type(url: str, title: str = "") -> str`

**説明**:
```
物件タイプを判定  Args: url: 物件URL
```

#### `calculate_property_age(construction_year: Optional[int]) -> Optional[int]`

**説明**:
```
築年数を計算  Args: construction_year: 建築年（西暦）
```

#### `format_price_display(price: Optional[float]) -> str`

**説明**:
```
価格を表示用にフォーマット  Args: price: 価格（円単位）
```

#### `normalize_property_type(property_type: str) -> str`

**説明**:
```
物件種別を正規化  Args: property_type: 物件種別文字列
```

---

## 📁 exceptions.py

- **サイズ**: 0KB
- **行数**: 1行
- **総関数数**: 0個

---

## 📁 config.py

- **サイズ**: 0KB
- **行数**: 1行
- **総関数数**: 0個

---

## 📁 scrapers_common.py

### 📝 ファイル説明
```
REAスクレイピング共通処理
URL管理、データ抽出、エラーハンドリング等の共通機能
```

- **サイズ**: 15KB
- **行数**: 513行
- **総関数数**: 23個

### 📦 インポート詳細

- `import pickle`
- `import random`
- `import re`
- `import time`
- `from datetime import datetime`
- `from pathlib import Path`
- `from typing import Any, Dict, List, Optional, Set`
- `from urllib.parse import urljoin`
- `from bs4 import BeautifulSoup`
- `from loguru import logger`
- `from shared.formatters import (`
- `from shared.formatters import clean_text_content`
- `from shared.formatters import extract_listing_id`

### 🏗️ クラス詳細

#### `URLQueue` クラス

**説明**:
```
URL収集と管理を行う汎用クラス
    複数のスクレイピングサイトで共通利用可能
```

**メソッド一覧**: 9個

- `__init__(self, site_name: str, cache_dir: str = "data/url_cache") `
  - 📝 Args:

- `_load_state(self) `
  - 📝 保存された状態を読み込む

- `save_state(self) `
  - 📝 現在の状態を保存

- `add_urls(self, urls: List[str]) -> int`
  - 📝 URLをキューに追加

- `get_next_batch(self, batch_size: int = 10) -> List[str]`
  - 📝 次のバッチを取得

- `mark_completed(self, url: str) `
  - 📝 URLを完了済みとしてマーク

- `mark_failed(self, url: str, error: str) `
  - 📝 URLを失敗としてマーク（ログ記録後、完了済みとして扱う）

- `get_stats(self) -> Dict[str, int]`
  - 📝 統計情報を取得

- `reset(self) `
  - 📝 キューをリセット（テスト用）

#### `RateLimiter` クラス

**説明**:
```
レート制限管理クラス
    サイトごとの適切な待機時間を管理
```

**メソッド一覧**: 3個

- `__init__(self, min_delay: float = 3.0, max_delay: float = 8.0) `
  - 📝 Args:

- `wait(self) `
  - 📝 適切な待機時間を取る

- `create_property_base_data(url: str, site_name: str) -> Dict[str, Any]`
  - 📝 物件データの基本構造を作成

### ⚙️ モジュールレベル関数

#### `__init__(self, min_delay: float = 3.0, max_delay: float = 8.0) `

**説明**:
```
Args: min_delay: 最小待機時間（秒） max_delay: 最大待機時間（秒）
```

#### `_load_state(self) `

**説明**:
```
保存された状態を読み込む
```

#### `save_state(self) `

**説明**:
```
現在の状態を保存
```

#### `add_urls(self, urls: List[str]) -> int`

**説明**:
```
URLをキューに追加  Args: urls: 追加するURLのリスト
```

#### `get_next_batch(self, batch_size: int = 10) -> List[str]`

**説明**:
```
次のバッチを取得  Args: batch_size: バッチサイズ
```

#### `mark_completed(self, url: str) `

**説明**:
```
URLを完了済みとしてマーク
```

#### `mark_failed(self, url: str, error: str) `

**説明**:
```
URLを失敗としてマーク（ログ記録後、完了済みとして扱う）  Args: url: 失敗したURL
```

#### `get_stats(self) -> Dict[str, int]`

**説明**:
```
統計情報を取得
```

#### `reset(self) `

**説明**:
```
キューをリセット（テスト用）
```

#### `wait(self) `

**説明**:
```
適切な待機時間を取る
```

#### `create_property_base_data(url: str, site_name: str) -> Dict[str, Any]`

**説明**:
```
物件データの基本構造を作成  Args: url: 物件URL
```

---

## 📁 database.py

### 📝 ファイル説明
```
REA シンプルデータベース接続

【重要】DB接続設定について
========================
このファイルは必ずプロジェクトルートの.envファイルから設定を読み込みます。
.envファイルの場所: /Users/yaguchimakoto/my_programing/REA/.env

.envファイルに以下の設定が必要です：

DB_HOST=localhost        # Docker PostgreSQL接続用
DB_PORT=5432            # PostgreSQLのポート
DB_NAME=real_estate_db  # データベース名
DB_USER=rea_user        # データベースユーザー名
DB_PASSWORD=rea_password # データベースパスワード

【共通ライブラリの仕様】
========================
- どこから実行しても同じ.envファイルを使用
- 設定の一元管理を実現
- 実行場所に依存しない安定した接続
- 全てのモジュールはこのライブラリを経由してDB接続する

【変更履歴】
========================
2025-07-23: プロジェクトルート固定化（技術的負債解消）
           - 実行場所による.env読み込みの差異を解消
           - DB接続の完全統一化を実現
```

- **サイズ**: 12KB
- **行数**: 378行
- **総関数数**: 18個

### 📦 インポート詳細

- `import os`
- `from pathlib import Path`
- `from typing import Any, Dict, List, Optional`
- `import psycopg2`
- `from psycopg2.extras import RealDictCursor`

### 🏗️ クラス詳細

#### `READatabase` クラス

**説明**:
```
シンプルなDB接続クラス

    REAプロジェクトの全てのDB接続を統一管理する共通ライブラリ。
    どのモジュールから使用しても同じ設定で接続できることを保証する。
```

**メソッド一覧**: 9個

- `_load_env(cls) `
  - 📝 プロジェクトルートの.envファイルを必ず読み込む

- `get_connection(cls) `
  - 📝 DB接続を取得

- `test_connection(cls) -> bool`
  - 📝 接続テスト

- `execute_query(cls, query: str, params: Optional[tuple] = None) -> List[tuple]`
  - 📝 クエリ実行（タプル形式）

- `get_all_tables(cls) -> List[str]`
  - 📝 テーブル一覧取得

- `get_table_info(cls, table_name: str) -> Dict[str, Any]`
  - 📝 テーブル情報取得

- `health_check(cls) -> Dict[str, Any]`
  - 📝 DB健康チェック

- `quick_test() `
  - 📝 接続テストのショートカット

- `get_tables() `
  - 📝 テーブル一覧取得のショートカット

### ⚙️ モジュールレベル関数

#### `_load_env(cls) `

**説明**:
```
プロジェクトルートの.envファイルを必ず読み込む  共通ライブラリの核心部分： - 常にプロジェクトルートの.envを使用 - どこから実行しても同じ設定を使用
```

#### `get_connection(cls) `

**説明**:
```
DB接続を取得  環境変数から接続情報を取得します。 必ずプロジェクトルートの.envファイルを読み込みます。
```

#### `test_connection(cls) -> bool`

**説明**:
```
接続テスト  DB接続が可能かテストします。 全モジュールで使用前にこのメソッドでテストすることを推奨。
```

#### `execute_query(cls, query: str, params: Optional[tuple] = None) -> List[tuple]`

**説明**:
```
クエリ実行（タプル形式）  基本的なSQL実行メソッド。結果はタプルのリストで返す。  Args:
```

#### `get_all_tables(cls) -> List[str]`

**説明**:
```
テーブル一覧取得  publicスキーマの全テーブルを取得。 DB構造の確認や仕様書生成で使用。
```

#### `get_table_info(cls, table_name: str) -> Dict[str, Any]`

**説明**:
```
テーブル情報取得  指定テーブルの詳細情報を取得。 カラム情報、レコード数などを含む。
```

#### `health_check(cls) -> Dict[str, Any]`

**説明**:
```
DB健康チェック  DB接続の詳細な状態を確認。 モニタリングやデバッグで使用。
```

#### `quick_test() `

**説明**:
```
接続テストのショートカット  既存コードとの互換性のため維持。 新規コードではREADatabase.test_connection()を推奨。
```

#### `get_tables() `

**説明**:
```
テーブル一覧取得のショートカット  既存コードとの互換性のため維持。 新規コードではREADatabase.get_all_tables()を推奨。
```

### 📊 定数

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

---

## 📁 system_utils.py

- **サイズ**: 0KB
- **行数**: 1行
- **総関数数**: 0個

---

## 📊 サマリー

- **分析ファイル数**: 11
- **総クラス数**: 3
- **総関数数**: 59
- **総行数**: 1522

---

*このドキュメントは自動生成されました（全関数検出版）*