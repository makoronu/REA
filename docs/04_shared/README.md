# 📚 REA 共通ライブラリ仕様

## 📋 概要
- **生成日時**: 2025-09-11 20:01:54
- **目的**: コード重複排除・統一性確保
- **ライブラリ数**: 11

## ✅ 実装済みライブラリ

### 🗄️ データベース関連
- **database.py**: ✅ 統一DB接続・操作システム
  - `READatabase.get_connection()` - 統一接続
  - `READatabase.health_check()` - 健康状態確認
  - `READatabase.get_all_tables()` - テーブル一覧
  - `READatabase.get_table_info()` - テーブル詳細
  - `READatabase.execute_query()` - クエリ実行

## 🎯 予定ライブラリ（Phase 2実装後）

### ⚙️ 設定管理
- **config.py**: 統一設定管理
- **constants.py**: 定数・設定値

### 🛠️ ユーティリティ
- **real_estate_utils.py**: 不動産業務専用関数
- **formatters.py**: フォーマット処理
- **system_utils.py**: システム共通処理

### 📝 ログ・エラー
- **logger.py**: 統一ログ管理
- **exceptions.py**: 統一エラー処理

## 🔧 使用例（database.py）

### 基本的な使用
```python
from shared.database import READatabase

# 接続テスト
if READatabase.test_connection():
    print("✅ DB接続成功")

# テーブル一覧取得
tables = READatabase.get_all_tables()
print(f"テーブル数: {len(tables)}")

# 健康チェック
health = READatabase.health_check()
print(f"応答時間: {health['response_time_ms']}ms")
```

### クエリ実行
```python
# 物件数確認
result = READatabase.execute_query("SELECT COUNT(*) FROM properties")
print(f"物件数: {result[0][0]}")

# 辞書形式で取得
properties = READatabase.execute_query_dict(
    "SELECT id, title, price FROM properties LIMIT 5"
)
for prop in properties:
    print(f"{prop['title']}: {prop['price']}円")
```

## 🔧 実装予定機能

### 不動産業務関数
```python
def format_price(price):
    """価格フォーマット: 12000000 → "1,200万円""""
    
def calculate_yield(price, rent):
    """利回り計算"""
    
def normalize_address(address):
    """住所正規化"""
    
def get_property_age(construction_date):
    """築年数計算"""
```

### システム共通関数
```python
def generate_property_id():
    """物件ID生成"""
    
def create_thumbnail(image_path):
    """サムネイル生成"""
    
def validate_property_data(data):
    """物件データ検証"""
```

## 📈 効果実績・予測
- **DB接続エラー**: 毎回発生 → ✅ 完全解決
- **コード重複**: 現在頻発 → 完全排除予定
- **開発効率**: 新機能開発10倍高速予定
- **保守性**: 修正1箇所で全体反映予定
- **品質**: 統一された高品質コード予定

## 🚀 next step
Phase 1（DB構造分析）完了後、技術的負債解消として実装予定
