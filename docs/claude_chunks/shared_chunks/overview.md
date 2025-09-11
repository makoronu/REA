# 🤖 Claude専用：REA共通ライブラリ情報

## 📚 実装済みライブラリ

### database.py（重要）
**目的**: DB接続問題の根本解決
**機能**:
- `READatabase.get_connection()` - 統一接続
- `READatabase.health_check()` - 健康状態確認
- `READatabase.get_all_tables()` - テーブル一覧
- `READatabase.test_connection()` - 接続テスト

**使用例**:
```python
from shared.database import READatabase

# 接続テスト
if READatabase.test_connection():
    print("✅ 接続成功")

# テーブル一覧
tables = READatabase.get_all_tables()
```

## 💡 重要な事実
- **問題**: 毎回DB接続でつまづく
- **解決**: shared/database.py で統一
- **効果**: エラー激減、開発効率向上

## 🔧 環境変数設定（忘れやすい）
```bash
export DATABASE_URL="postgresql://rea_user:rea_password@localhost/real_estate_db"
```

**これを忘れると接続失敗する！**
