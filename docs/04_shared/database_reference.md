# 📄 shared/database.py 詳細リファレンス

## 📋 ファイル情報
- **モジュール名**: shared.database
- **ファイルサイズ**: 12,387 bytes
- **行数**: 345
- **生成日時**: 2025-07-21 21:05:46

## 📝 ファイル説明
REA Database Connection System - 統一DB接続・管理システム
毎回のDB接続エラーを根本解決する共通ライブラリ

## 📦 インポート
- `import os`
- `import psycopg2`
- `import logging`
- `from typing import Optional`
- `from typing import Dict`
- `from typing import Any`
- `from typing import List`
- `from typing import Tuple`
- `from contextlib import contextmanager`
- `import time`
- `import json`
- `from pathlib import Path`
- `import re`

## 🏗️ クラス: READatabase

**行番号**: 16

**説明**: REA統一データベース接続・管理クラス

### メソッド

#### `__new__`

**行番号**: 23

**引数**:
- `cls`: Any

**説明**: 

#### `__init__`

**行番号**: 28

**引数**:
- `self`: Any

**説明**: 

#### `_setup_logger`

**行番号**: 34

**引数**:

**説明**: ログ設定

**デコレータ**: staticmethod

#### `load_config`

**行番号**: 46

**引数**:
- `cls`: Any

**戻り値**: Dict[str, str]

**説明**: 設定読み込み - 複数箇所から統一的に取得

**デコレータ**: classmethod

#### `_parse_database_url`

**行番号**: 90

**引数**:
- `cls`: Any
- `database_url`: str

**戻り値**: Optional[Dict[str, str]]

**説明**: DATABASE_URL をパースして設定辞書に変換

**デコレータ**: classmethod

#### `_load_env_file`

**行番号**: 113

**引数**:
- `cls`: Any

**戻り値**: Optional[Dict[str, str]]

**説明**: 複数の.envファイルから設定読み込み

**デコレータ**: classmethod

#### `_validate_config`

**行番号**: 145

**引数**:
- `config`: Dict[str, str]

**戻り値**: bool

**説明**: 設定の妥当性チェック

**デコレータ**: staticmethod

#### `get_connection`

**行番号**: 151

**引数**:
- `cls`: Any
- `auto_retry`: bool

**戻り値**: psycopg2.extensions.connection

**説明**: 統一DB接続取得 - 自動リトライ機能付き

**デコレータ**: classmethod

#### `get_cursor`

**行番号**: 187

**引数**:
- `cls`: Any

**説明**: カーソル取得 - with文で自動クローズ

**デコレータ**: classmethod, contextmanager

#### `execute_query`

**行番号**: 197

**引数**:
- `cls`: Any
- `query`: str
- `params`: Optional[tuple]

**戻り値**: List[tuple]

**説明**: クエリ実行 - 結果取得

**デコレータ**: classmethod

#### `execute_query_dict`

**行番号**: 206

**引数**:
- `cls`: Any
- `query`: str
- `params`: Optional[tuple]

**戻り値**: List[Dict[str, Any]]

**説明**: クエリ実行 - 辞書形式結果取得

**デコレータ**: classmethod

#### `get_table_info`

**行番号**: 217

**引数**:
- `cls`: Any
- `table_name`: str

**戻り値**: Dict[str, Any]

**説明**: テーブル情報取得

**デコレータ**: classmethod

#### `get_all_tables`

**行番号**: 247

**引数**:
- `cls`: Any

**戻り値**: List[str]

**説明**: 全テーブル一覧取得

**デコレータ**: classmethod

#### `health_check`

**行番号**: 259

**引数**:
- `cls`: Any

**戻り値**: Dict[str, Any]

**説明**: DB健康状態チェック

**デコレータ**: classmethod

#### `test_connection`

**行番号**: 293

**引数**:
- `cls`: Any

**戻り値**: bool

**説明**: 接続テスト - 簡単な成功/失敗判定

**デコレータ**: classmethod


## ⚙️ 関数: quick_query

**行番号**: 302

**引数**:
- `sql`: str
- `params`: Optional[tuple]

**戻り値**: List[Dict[str, Any]]

**説明**: クイッククエリ実行


## ⚙️ 関数: quick_test

**行番号**: 306

**引数**:

**戻り値**: bool

**説明**: クイック接続テスト


## ⚙️ 関数: get_tables

**行番号**: 310

**引数**:

**戻り値**: List[str]

**説明**: クイックテーブル一覧

